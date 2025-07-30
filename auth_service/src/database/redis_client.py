import json

from redis.asyncio import Redis

from core import db_config, logger
from utils.custom_exception import RedisError


class RedisClient:
    """Асинхронный клиент Redis."""

    def __init__(self) -> None:
        self._client = Redis(
            password=db_config.redis_password,
            db=db_config.redis_auth_db,
            host=db_config.redis_host,
            port=db_config.redis_port,
            decode_responses=True,
        )

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
        key: str,
        as_dict: bool = False,
    ) -> dict[str, str | int] | str | None:
        """
        Прослойка - получение значений из Redis.

        @type key: str
        @param key:
        @type as_dict: bool
        @param as_dict: Флаг - получаемые значения требуется сериализовать.

        @rtype value: dict[str, str | int] | str | None
        @return value:
        """
        try:
            value = await self._client.get(key)

        except Exception as ex:
            logger.error(f"Error get data from Redis: {ex}")
            raise RedisError()

        if as_dict:
            try:
                value = json.loads(value)

            except (json.JSONDecodeError, TypeError) as ex:
                logger.warning(f"Can't parse str as dict: {ex}")

        return value

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

async def get_redis_client() -> RedisClient:
    """
    Получение(инициализация) клиента Redis.

    @rtype: RedisClient
    @return:
    """
    return RedisClient()
