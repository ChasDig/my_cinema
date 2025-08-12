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
        default=1 * 250,
        alias="ETL_CINEMA_SELECT_LIMIT",
    )

    @computed_field
    @property
    def base_dir(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config = Settings()
db_config = DBSettings()
