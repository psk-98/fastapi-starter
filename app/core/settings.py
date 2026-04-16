import secrets
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24 * 8
    )  # 8 days=60 minutes * 24 hours * 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    ENV: Literal["local", "staging", "production"] = "local"
    DATABASE_NAME: str = ""
    DATABASE_USER: str
    DATABASE_PASSWORD: str = ""
    DATABASE_HOST: str
    DATABASE_PORT: int = 6543

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=self.DATABASE_NAME,
        )


settings = Settings()  # type: ignore
