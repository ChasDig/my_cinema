import os

from dotenv import find_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = find_dotenv()


class Settings(BaseSettings):
    """Конфигурации - базовые."""

    # Meta
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    service_name: str = Field(default="auth_service")
    log_format: str = Field(
        default="%(asctime)s - %(levelname)s - %(message)s",
    )

    @computed_field
    @property
    def base_dir(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # WS
    ws_host: str = Field(default="127.0.0.1", alias="WS_HOST")
    ws_port: int = Field(default=8765, alias="WS_PORT")

    # RedisDB
    redis_password: str = Field(default="redis_pass", alias="REDIS_PASSWORD")
    redis_auth_db: int = Field(default=1, alias="WS_REDIS_DB")
    redis_host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_max_connections_pool: int = Field(
        default=50,
        alias="WS_REDIS_MAX_CONNECTION_POOL",
    )


config = Settings()
