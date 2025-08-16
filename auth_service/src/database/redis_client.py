import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from core.app_config import db_config
from core.app_logger import logger
from redis.asyncio import ConnectionPool, Redis
from utils.custom_exception import RedisError

redis_pool = ConnectionPool(
    password=db_config.redis_password,
    db=db_config.redis_auth_db,
    host=db_config.redis_host,
    port=db_config.redis_port,
    decode_responses=True,
    max_connections=db_config.redis_max_connections_pool,
)


class RedisClient:
    """Асинхронный клиент Redis."""

    def __init__(self) -> None:
        self._client = Redis(connection_pool=redis_pool)

    async def close(self) -> None:
        await self._client.close()

    async def ping(self) -> None:
        await self._client.ping()

    async def set(
        self,
        key: str,
        value: str | dict[str, str | int],
        ttl: int | None = None,
    ) -> None:
        """
        Прослойка - вставка значений в Redis.

        @type key: str
        @param key:
        @type value: str | dict[str, str | int]
        @param value:
        @type ttl: int | None
        @param ttl:

        @rtype: None
        @return:
        """
        if isinstance(value, dict):
            value = json.dumps(value)

        try:
            await self._client.set(key, value, ex=ttl)

        except Exception as ex:
            logger.error(f"Error set data in Redis: {ex}")
            raise RedisError()

    async def get(
        self,
        key: str | Any,
        as_dict: bool = False,
    ) -> dict[str, str | int] | str | None:
        """
        Прослойка - получение значений из Redis.

        @type key: str | bytes | bytearray
        @param key:
        @type as_dict: bool
        @param as_dict: Флаг - для получаемых значений требуется сериализация.

        @rtype value: dict[str, str | int] | str | None
        @return value:
        """
        try:
            value = await self._client.get(key)

        except Exception as ex:
            logger.error(f"Error get data from Redis: {ex}")
            raise RedisError()

        if as_dict and value is not None:
            try:
                value = json.loads(value)

            except (json.JSONDecodeError, TypeError) as ex:
                logger.warning(f"Can't parse str as dict: {ex}")

        return value  # type: ignore

    async def delete(self, key: str) -> None:
        """
        Прослойка - удаление значений из Redis.

        @type key: str
        @param key:

        @rtype: None
        @return:
        """
        try:
            await self._client.delete(key)

        except Exception as ex:
            logger.error(f"Error delete data from Redis: {ex}")
            raise RedisError()


@asynccontextmanager
async def redis_context_manager() -> AsyncGenerator[RedisClient, Any]:
    """
    Асинхронный контекстный менеджер для получения активного клиента Redis.

    @rtype: AsyncGenerator[RedisClient, Any]
    @return:
    """
    client = RedisClient()

    try:
        yield client

    finally:
        await client.close()


async def get_redis_client() -> AsyncGenerator[RedisClient, Any]:
    """
    Асинхронный генератор для получения активной сессии с Redis.
    Применение:
    - Обертка для Dependency в FastAPI (раскрытие асинхронных генераторов,
    аналогия - anext).

    @rtype client: AsyncGenerator[RedisClient, Any]
    @return client:
    """
    async with redis_context_manager() as client:
        yield client
