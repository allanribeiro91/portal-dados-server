from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portal de Dados API"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url_env: str | None = Field(default=None, validation_alias="DATABASE_URL")
    db_dialect: str = "postgresql"
    db_driver: str = "psycopg"
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = ""
    db_database: str = "dbportaldados"
    db_schema: str = "scportaldados"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10


    jwt_secret_key: str = "ALTERE_ESTA_CHAVE"
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    jwt_issuer: str = "portal-dados-api"
    jwt_audience: str = "portal-dados-frontend"
    jwt_refresh_cookie_name: str = "portal_refresh_token"
    jwt_refresh_cookie_secure: bool = False
    jwt_refresh_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    @field_validator("db_schema")
    @classmethod
    def validate_schema(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or not normalized.replace("_", "").isalnum() or normalized[0].isdigit():
            raise ValueError("DB_SCHEMA deve ser um identificador SQL válido")
        return normalized

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url_env:
            url = self.database_url_env
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            return url

        username = quote_plus(self.db_username)
        password = quote_plus(self.db_password)
        credentials = f"{username}:{password}" if password else username
        return (
            f"{self.db_dialect}+{self.db_driver}://{credentials}"
            f"@{self.db_host}:{self.db_port}/{self.db_database}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
