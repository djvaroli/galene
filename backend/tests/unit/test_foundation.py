from pathlib import Path

import pytest
from alembic import command
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text

from app.adapters.database import create_database, migration_config, require_current_schema
from app.bootstrap import create_app
from app.settings import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    (tmp_path / "db").mkdir()
    return Settings(app_env="test", storage_dir=tmp_path)


def upgrade(settings: Settings) -> None:
    engine = create_database(settings.database_path)
    with engine.begin() as connection:
        config = migration_config()
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    engine.dispose()


def test_migrations_are_repeatable_and_sqlite_connections_are_configured(
    settings: Settings,
) -> None:
    upgrade(settings)
    upgrade(settings)
    engine = create_database(settings.database_path)
    require_current_schema(engine)
    with engine.connect() as connection:
        for pragma, expected in {
            "journal_mode": "wal",
            "foreign_keys": 1,
            "busy_timeout": 5000,
            "synchronous": 2,
        }.items():
            assert connection.execute(text(f"PRAGMA {pragma}")).scalar() == expected
    engine.dispose()


def test_api_refuses_unmigrated_database(settings: Settings) -> None:
    with pytest.raises(RuntimeError, match="migration service"):
        with TestClient(create_app(settings)):
            pass


def test_api_health_and_json_404(settings: Settings) -> None:
    upgrade(settings)
    with TestClient(create_app(settings)) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert client.get("/api/v1/info").json() == {"name": "Galene", "stage": "foundation"}
        missing = client.get("/api/v1/missing")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "not_found"
        assert missing.json()["request_id"] == missing.headers["X-Request-ID"]
        assert missing.headers["Cache-Control"] == "no-store"


def test_schema_change_fails_readiness_and_subsequent_startup(settings: Settings) -> None:
    upgrade(settings)
    with TestClient(create_app(settings)) as client:
        engine = create_database(settings.database_path)
        with engine.begin() as connection:
            connection.execute(text("UPDATE alembic_version SET version_num = 'future_revision'"))
        engine.dispose()
        assert client.get("/health/ready").status_code == 503
        assert client.get("/health/live").status_code == 200
    with pytest.raises(RuntimeError, match="incompatible"):
        with TestClient(create_app(settings)):
            pass


def test_production_is_unavailable_before_authentication(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GALENE_APP_ENV", "production")
    with pytest.raises(ValidationError):
        Settings()
