import os
import sqlite3
from pathlib import Path

import httpx


def test_edge_serves_ui_assets_api_and_errors() -> None:
    with httpx.Client(base_url="http://nginx:8080", timeout=10) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Galene" in page.text
        assert 'id="root"' in page.text
        assert page.headers["X-Content-Type-Options"] == "nosniff"
        assert "frame-ancestors 'none'" in page.headers["Content-Security-Policy"]
        assert client.get("/rooms/future-route").text == page.text
        assert client.get("/assets/missing.js").status_code == 404
        assert client.get("/api/v1/info").json() == {"name": "Galene", "stage": "foundation"}
        for route in ("/api", "/api/missing", "/api/v1/missing"):
            response = client.get(route)
            assert response.status_code == 404
            assert response.json()["error"]["code"] == "not_found"
        for route in ("/health", "/health/live", "/health/ready", "/openapi.json"):
            assert client.get(route).status_code == 404


def test_edge_rejects_oversized_body() -> None:
    response = httpx.post("http://nginx:8080/api/v1/missing", content=b"x" * (21 * 1024 * 1024 + 1))
    assert response.status_code == 413


def test_internal_api_readiness() -> None:
    assert httpx.get("http://api:8000/health/ready").json() == {"status": "ok"}


def test_database_and_media_survive_service_recreation() -> None:
    # Synthetic records belong only to disposable test volumes.
    storage = Path(os.environ["GALENE_STORAGE_DIR"])
    with sqlite3.connect(storage / "db" / "inventory.sqlite3") as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            "0001_foundation",
        )
        assert connection.execute("SELECT value FROM persistence_probe").fetchone() == (
            "synthetic persistence check",
        )
    assert (storage / "media" / "probe.txt").read_text() == "synthetic media check"
