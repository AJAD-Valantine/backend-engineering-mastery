from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    db_engine: str = "postgresql+psycopg"
    db_username: str = "postgres"
    db_password: SecretStr
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "collection_ops_db"

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername=self.db_engine,
            username=self.db_username,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    DEFAULT_SORT: str = "-publish_date,book_id"
    MAX_SORT_FIELDS: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]

