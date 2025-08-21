import os
import pathlib

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
        alias="CINEMA_POSTGRES_DRIVERNAME",
    )
    pg_database: str = Field(default="cinema_db", alias="CINEMA_POSTGRES_DB")
    pg_username: str = Field(
        default="cinema_user",
        alias="CINEMA_POSTGRES_USER",
    )
    pg_password: str = Field(alias="CINEMA_POSTGRES_PASSWORD")
    pg_host: str = Field(default="127.0.0.1", alias="POSTGRES_HOST")
    pg_port: int = Field(default=5432, alias="POSTGRES_PORT")

    pg_engine_echo: bool = Field(
        default=False,
        description="Log level",
        alias="CINEMA_POSTGRES_ENGINE_ECHO",
    )
    pg_engine_pool_pre_ping: bool = Field(
        default=True,
        description="Check connection to DB before use",
        alias="CINEMA_POSTGRES_ENGINE_POOL_PRE_PING",
    )
    pg_engine_pool_recycle: int = Field(
        default=3600,
        description="TTL active connection to DB",
        alias="CINEMA_POSTGRES_ENGINE_POOL_RECYCLE",
    )
    pg_engine_pool_size: int = Field(
        default=10,
        alias="CINEMA_POSTGRES_ENGINE_POOL_SIZE",
    )
    pg_engine_max_overflow: int = Field(
        default=10,
        description="Pool size over 'CINEMA_POSTGRES_ENGINE_POOL_SIZE'",
        alias="CINEMA_POSTGRES_ENGINE_MAX_OVERFLOW",
    )

    @computed_field
    @property
    def pg_url_connection(self) -> str:
        return (
            f"{self.pg_drivername}://{self.pg_username}:"
            f"{self.pg_password}@{self.pg_host}:"
            f"{self.pg_port}/{self.pg_database}"
        )

    # ES:
    elastic_schema: str = Field(default="http", alias="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_host: str = Field(default="127.0.0.1", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_password: str = Field(alias="ELASTIC_PASSWORD")

    es_indexes_path_: list[tuple[str, str]] | None = Field(default=None)

    @computed_field
    @property
    def es_indexes_path(self) -> list[tuple[str, str]]:
        if self.es_indexes_path_ is None:
            current_dir = pathlib.Path(__file__).parent.parent
            ind_dir = current_dir / "models" / "elasticsearch_indexes"

            self.es_indexes_path_ = [
                (str(ind_dir / f.name), f.name.split(".")[0])
                for f in pathlib.Path(ind_dir).glob("*.json")
                if f.is_file()  # noqa: E501
            ]

        return self.es_indexes_path_

    @computed_field
    @property
    def elastic_url(self) -> str:
        return f"{self.elastic_schema}://{self.elastic_host}:{self.elastic_port}/"  # noqa: E501


class Settings(BaseSettings):
    """Конфигурации - базовые."""

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Meta
    service_name: str = Field(default="etl_service")
    log_format: str = Field(
        default="%(asctime)s - %(levelname)s - %(message)s",
    )

    # ETL
    etl_select_limit: int = Field(
        default=1_000,
        alias="ETL_CINEMA_SELECT_LIMIT",
    )
    etl_task_trigger: str = Field(
        default="interval",
        alias="ETL_CINEMA_TASK_TRIGGER",
    )
    etl_movies_task_interval_sec: int = Field(
        default=1 * 60,
        alias="ETL_CINEMA_TASK_INTERVAL_SEC",
    )
    etl_movies_select_limit: int = Field(
        default=1 * 500,
        alias="ETL_CINEMA_SELECT_LIMIT",
    )

    @computed_field
    @property
    def base_dir(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config = Settings()
db_config = DBSettings()
