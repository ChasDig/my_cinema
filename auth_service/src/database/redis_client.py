import json

from redis.asyncio import Redis

from core import db_config, logger
from utils.custom_exception import RedisError


class RedisClient:

    def __init__(self) -> None:
        self._client = Redis(
            username=db_config.redis_username,
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
        ex = None,
    ) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)

        try:
            await self._client.set(key, value, ex=ex)

        except Exception as ex:
            logger.error(f"Error set data in Redis: {ex}")
            raise RedisError()

    async def get(
        self,
        key: str,
        as_dict: bool = False,
    ) -> dict[str, str | int] | str:
        value = await self._client.get(key)

        if as_dict:
            try:
                value = json.loads(value)

            except (json.JSONDecodeError, TypeError) as ex:
                logger.warning(f"Can't parse str as dict: {ex}")

        return value


redis_async_client = RedisClient()
