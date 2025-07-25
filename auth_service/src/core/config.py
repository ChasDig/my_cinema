import os

from dotenv import find_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = find_dotenv()


class DBSettings(BaseSettings):
    """Конфигурации - Базы Данных."""

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

    # RedisDB
    redis_password: str = Field(alias="AUTH_REDIS_PASSWORD")
    redis_auth_db: int = Field(default=0, alias="AUTH_REDIS_DB")
    redis_host: str = Field(default="127.0.0.1", alias="AUTH_REDIS_HOST")
    redis_port: int = Field(default=6379, alias="AUTH_REDIS_PORT")


class CryptoSettings(BaseSettings):
    """Конфигурации - чувствительные данные (шифрование/хеширование)."""

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    length_hash: int = Field(default=32, alias="AUTH_LENGTH_HASH_PASSWORD")
    count_iter: int = Field(default=100_000, alias="AUTH_COUNT_HASH_ITER")
    salt_length_bytes: int = Field(default=16, alias="AUTH_SALT_BYTE_LENGTH")
    nonce_length_bytes: int = Field(default=12, alias="AUTH_NONCE_BYTE_LENGTH")

    token_secret: str = Field(alias="AUTH_TOKEN_SECRET")
    access_token_exp_min: int = Field(
        default=30,
        alias="AUTH_ACCESS_TOKEN_EXP_MIN",
    )
    refresh_token_exp_days: int = Field(
        default=7,
        alias="AUTH_REFRESH_TOKEN_EXP_DAYS",
    )
    token_algorithm: str = Field(default="HS256", alias="AUTH_TOKEN_ALGORITHM")

    password_delimiter: str = Field(
        default="$",
        alias="AUTH_PASSWORD_DELIMITER",
    )
    email_master_password: str = Field(alias="AUTH_EMAIL_MASTER_PASSWORD")


class Settings(BaseSettings):
    """Конфигурации - базовые."""
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
