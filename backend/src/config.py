from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str
    pgport: int = Field(default=5432, ge=1, le=65535)

    celery_broker_url: str

    storage_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent / "storage" / "files"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.pgport}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
