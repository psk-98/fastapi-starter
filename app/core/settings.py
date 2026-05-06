import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


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
    FRONTEND_HOST: str = "http://localhost:3000"  # next js frontend
    ENV: Literal["local", "staging", "production"] = "local"

    CELERY_BROKER_URI: str = "redis://localhost:6379"

    DATABASE_NAME: str = ""
    DATABASE_USER: str
    DATABASE_PASSWORD: str = ""
    DATABASE_HOST: str
    DATABASE_DOCKER_NETWORK_HOST: str
    DATABASE_PORT: int = (
        6543  # for postgre, this is what i usually use for docker containers
    )

    DATABASE_DOCKER_NETWORK_PORT: int = 5432  # for postgre

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=(
                self.DATABASE_HOST
                if self.ENV == "local"
                else self.DATABASE_DOCKER_NETWORK_HOST
            ),
            port=(
                self.DATABASE_PORT
                if self.ENV == "local"
                else self.DATABASE_DOCKER_NETWORK_PORT
            ),
            path=self.DATABASE_NAME,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_DOCKER_NETWORK_HOST,
            port=self.DATABASE_DOCKER_NETWORK_PORT,
            path=self.DATABASE_NAME,
        )

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 60

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


settings = Settings()  # type: ignore
