from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )

    # Database
    db_engine: str = "postgresql+psycopg"
    db_username: str = "postgres"
    db_password: SecretStr
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "session_auth_db"

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

    # Security
    password_reset_expire_minutes: int = 15
    email_verification_token_expire_days: int = 1
    frontend_url: str = "http://localhost:3000"
    redis_url: str = "redis://localhost:6379"
    session_expire_seconds: int = 1800
    session_cookie_name: str = "session_id"
    session_prefix: str = "session:"
    sessions_prefix: str = "session_ids:"

    # Email
    smtp_port: int = 1025
    smtp_host: str = "localhost"

    # State Parameter
    state_cookie_name: str = "oauth_state"
    state_max_age: int = 600
    state_secret_key: SecretStr

    # GOOGLE OAuth 2.0 Credentials
    google_client_id: str = "89439520050-bhorqqitb9bt21oidp0i86ehp1ckudb4.apps.googleusercontent.com"
    google_client_secret: SecretStr
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_user_info_url: str = "https://openid-connect.googleapis.com/v1/userinfo"


@lru_cache
def get_settings() -> Settings:
    return Settings() # pyright: ignore[reportCallIssue]
