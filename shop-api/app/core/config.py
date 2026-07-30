from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )

    # Database

    db_engine : str
    db_username : SecretStr
    db_password : SecretStr
    db_host : str
    db_port : int
    db_name : str

    @property
    def SQLALCHEMY_DATABASE_URL(self):
        return  f"""{self.db_engine}://
                    {self.db_username.get_secret_value()}:
                    {self.db_password.get_secret_value()}@
                    {self.db_host}:
                    {self.db_port}/
                    {self.db_name}"""

    # Auth

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()  # type: ignore[call-arg]