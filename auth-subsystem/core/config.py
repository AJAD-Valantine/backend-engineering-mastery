from pathlib import Path

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
    jwt_secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    password_reset_expire_minutes: int = 15
    email_verification_token_expire_days: int = 1
    frontend_url: str = "http://localhost:3000"

    # State Parameter
    state_cookie_name: str = "oauth_state"
    state_max_age: int = 600
    state_secret_key: SecretStr

    # Email
    smtp_port: int
    smtp_host: str

    # OAuth 2.0 Credentials
    google_client_id: str
    google_client_secret: SecretStr = SecretStr("")
    google_redirect_uri: str
    google_auth_url: Path = Path("https://accounts.google.com/o/oauth2/v2/auth?")
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_user_info_url: str = "https://openid-connect.googleapis.com/v1/userinfo"

    github_client_id: str
    github_client_secret: SecretStr = SecretStr("")
    github_redirect_uri: str
