from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )

    # Database
    database_url: str = "sqlite:///./app.db"

    # Security
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    password_reset_expire_minutes: int = 15
    email_verification_token_expire_days: int = 1
    frontend_url: str = "http://localhost:3000"

    # Email
    smtp_port: int
    smtp_host: str
