import functools

from database import (
    pg_session_factory,
    redis_context_manager,
    redis_pool,
)
from fastapi import FastAPI
from sqlalchemy import text
from utils.custom_exception import StartUpError

from .app_logger import logger


class StartUpEvents:
    """Класс реализующий события, при запуске сервиса."""

    @classmethod
    async def exec(cls) -> None:
        for name, method in cls.events.items():
            try:
                await method()
                logger.info(f"StartUp event '{name}' was success...")

            except Exception as ex:
                raise StartUpError(f"Error StartUp event '{name}': {ex}")

    @staticmethod
    async def check_postgres() -> None:
        async with pg_session_factory.context_session() as pg_session:
            query = await pg_session.execute(text("SELECT 1;"))
            query.one_or_none()

    @staticmethod
    async def check_redis() -> None:
        async with redis_context_manager() as redis_client:
            await redis_client.ping()

    events = {
        check_postgres.__name__: check_postgres,
        check_redis.__name__: check_redis,
    }


class ShutDownEvents:
    """Класс реализующий события, при остановке сервиса."""

    @classmethod
    async def exec(cls) -> None:
        for name, method in cls.events.items():
            try:
                await method()
                logger.info(f"ShutDown event '{name}' was success...")

            except Exception as ex:
                logger.error(f"Error ShutDown event '{name}': {ex}")

    @staticmethod
    async def close_redis_connection_pool() -> None:
        if redis_pool:
            await redis_pool.disconnect()

    events = {
        close_redis_connection_pool.__name__: close_redis_connection_pool,
    }


def register_events(app: FastAPI) -> None:
    app.add_event_handler(
        "startup",
        functools.partial(StartUpEvents.exec),
    )
    app.add_event_handler(
        "shutdown",
        functools.partial(ShutDownEvents.exec),
    )
