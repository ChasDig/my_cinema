from fastapi import status, HTTPException

from core import logger
from database.redis_client import RedisClient
from utils import Tokenizer
from models.api_models import Tokens
from models.pg_models import Users
from utils.custom_exception import RedisError


class TokensRefreshMixin:
    """Mixin - процесс обновления jwt-токенов."""

    @staticmethod
    async def _insert_tokens(
        tokens: Tokens,
        user: Users,
        redis_client: RedisClient,
        user_agent: str,
    ) -> None:
        """
        Вставка токенов в Redis.

        @type tokens: Tokens
        @param tokens:
        @type user: Users
        @param user:
        @type redis_client: RedisClient
        @param redis_client:
        @type user_agent: str
        @param user_agent:

        @rtype: None
        @return:
        """
        for_gen = f"{user.nickname} / {user_agent}"

        try:
            await redis_client.set(
                key=Tokenizer.token_key_template.format(
                    user_id=user.id,
                    user_agent=user_agent,
                    token_type=tokens.access_token.type,
                ),
                value=tokens.access_token.token,
                ttl=tokens.access_token.ttl,
            )
            logger.info(
                f"{tokens.access_token.type} token was gen for {for_gen}"
            )

            await redis_client.set(
                key=Tokenizer.token_key_template.format(
                    user_id=user.id,
                    user_agent=user_agent,
                    token_type=tokens.refresh_token.type,
                ),
                value=tokens.refresh_token.token,
                ttl=tokens.refresh_token.ttl,
            )
            logger.info(
                f"{tokens.refresh_token.type} token was gen for {for_gen}"
            )

        except RedisError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error gen tokens",
            )

    @staticmethod
    async def _delete_tokens(
        user_id: str,
        redis_client: RedisClient,
        user_agent: str,
    ) -> None:
        """
        Удаление токенов из Redis.

        @type user_id: str
        @param user_id:
        @type redis_client: RedisClient
        @param redis_client:
        @type user_agent: str
        @param user_agent:

        @rtype: None
        @return:
        """
        try:
            await redis_client.delete(
                key=Tokenizer.token_key_template.format(
                    user_id=user_id,
                    user_agent=user_agent,
                    token_type="*",
                ),
            )

        except RedisError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error delete tokens",
            )
