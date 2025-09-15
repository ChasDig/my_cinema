from core.app_logger import logger
from database.redis_client import RedisClient
from fastapi import HTTPException, status
from models.api_models.external import Tokens
from utils import Hasher, Tokenizer
from utils.custom_exception import NotFoundError, RedisError


class TokensRefreshMixin:
    """Mixin - процесс обновления jwt-токенов."""

    @staticmethod
    async def _insert_tokens(
        tokens: Tokens,
        user_id: str,
        redis_client: RedisClient,
        user_agent: str,
        user_email_hash: str | None = None,
    ) -> None:
        """
        Вставка токенов в Redis.

        @type tokens: Tokens
        @param tokens:
        @type user_id: str
        @param user_id:
        @type redis_client: RedisClient
        @param redis_client:
        @type user_agent: str
        @param user_agent:
        @type user_agent: str
        @param user_agent:

        @rtype: None
        @return:
        """
        for_ = f"{user_agent} | {user_email_hash if user_email_hash else '-'}"

        try:
            await redis_client.set(
                key=Tokenizer.token_key_template.format(
                    user_id=user_id,
                    user_agent=user_agent,
                    token_type=tokens.access_token.type,
                ),
                value=tokens.access_token.token,
                ttl=tokens.access_token.ttl,
            )
            logger.info(f"{tokens.access_token.type} token gen for {for_}")

            await redis_client.set(
                key=Tokenizer.token_key_template.format(
                    user_id=user_id,
                    user_agent=user_agent,
                    token_type=tokens.refresh_token.type,
                ),
                value=tokens.refresh_token.token,
                ttl=tokens.refresh_token.ttl,
            )
            logger.info(f"{tokens.refresh_token.type} token gen for {for_}")

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

    @staticmethod
    async def _check_password_by_hash(
        incoming_password: str,
        user_hash_password: str,
    ) -> None:
        """
        Проверка пароля в открытом виде на соответствие hash-паролю.

        @type incoming_password: str
        @param incoming_password: Пароль (в открытом виде).
        @type user_hash_password: str
        @param user_hash_password: Hash-пароль.

        @rtype: None
        @return:
        """
        if not Hasher.check_password_by_hash(
            incoming_password=incoming_password,
            user_hash_password=user_hash_password,
        ):
            raise NotFoundError(detail="Not correct user email or password")
