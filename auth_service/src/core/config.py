import os
import pathlib

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(pathlib.Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8",
    )

    # Meta
    service_name: str = "auth_service"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(pathlib.Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8",
    )

    # PostgresDB
    pg_drivername: str = Field(
        default="postgresql+asyncpg",
        alias="AUTH_POSTGRES_DRIVERNAME",
    )
    pg_database: str = Field(default="auth_db", alias="AUTH_POSTGRES_DB")
    pg_username: str = Field(
        default="auth_service",
        alias="AUTH_POSTGRES_USER",
    )
    pg_password: str = Field(alias="AUTH_POSTGRES_PASSWORD")
    pg_host: str = Field(default="127.0.0.1", alias="AUTH_POSTGRES_HOST")
    pg_port: int = Field(default=5432, alias="AUTH_POSTGRES_PORT")

    pg_engine_echo: bool = Field(
        default=False,
        description="Log level",
        alias="AUTH_POSTGRES_ENGINE_ECHO",
    )
    pg_engine_pool_pre_ping: bool = Field(
        default=True,
        description="Check connection to DB before use",
        alias="AUTH_POSTGRES_ENGINE_POOL_PRE_PING",
    )
    pg_engine_pool_recycle: int = Field(
        default=3600,
        description="TTL active connection to DB",
        alias="AUTH_POSTGRES_ENGINE_POOL_RECYCLE",
    )
    pg_engine_pool_size: int = Field(
        default=10,
        alias="AUTH_POSTGRES_ENGINE_POOL_SIZE",
    )
    pg_engine_max_overflow: int = Field(
        default=10,
        description="Pool size over 'AUTH_POSTGRES_ENGINE_POOL_SIZE'",
        alias="AUTH_POSTGRES_ENGINE_MAX_OVERFLOW",
    )

    @computed_field
    @property
    def pg_url_connection(self) -> str:
        return (
            f"{self.pg_drivername}://{self.pg_username}:"
            f"{self.pg_password}@{self.pg_host}:"
            f"{self.pg_port}/{self.pg_database}"
        )


class Settings(Base, DBSettings):
    pass


config = Settings()
