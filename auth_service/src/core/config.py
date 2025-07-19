import os
import pathlib

from dotenv import find_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = find_dotenv()


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
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


class CryptoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    length_hash: int = Field(default=32, alias="AUTH_LENGTH_HASH_PASSWORD")
    count_iter: int = Field(default=100_000, alias="AUTH_COUNT_HASH_ITER")

    email_master_password: str = Field(default="123", alias="AUTH_EMAIL_MASTER_PASSWORD")  # TODO:

    @computed_field
    @property
    def email_master_password_bytes(self) -> bytes:
        return bytes(self.email_master_password, "utf-8")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Meta
    service_name: str = "auth_service"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"


config = Settings()
db_config = DBSettings()
crypto_config = CryptoSettings()
