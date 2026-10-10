from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GALENE_")

    # Production becomes available when owner authentication is implemented.
    app_env: Literal["development", "test"] = "development"
    storage_dir: Path = Path("/data")

    @property
    def database_path(self) -> Path:
        return self.storage_dir / "db" / "inventory.sqlite3"
