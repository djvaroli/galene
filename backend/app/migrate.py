from alembic import command

from app.adapters.database import create_database, migration_config
from app.settings import Settings


def main() -> None:
    settings = Settings()
    engine = create_database(settings.database_path)
    try:
        with engine.begin() as connection:
            config = migration_config()
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
