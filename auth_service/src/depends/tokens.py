from fastapi import Cookie, Depends, HTTPException, status

from models.api_models import TokenPayload
from utils import Tokenizer
from models.enums import TokenType
from depends import get_user_agent
from database.redis_client import RedisClient, get_redis_client


async def check_refresh_token(
    refresh_token: str = Cookie(None, alias=TokenType.refresh.name),
    redis_client: RedisClient = Depends(get_redis_client),
    user_agent: str = Depends(get_user_agent),
) -> TokenPayload:
    """
    Проверка Refresh-токена.

    @type refresh_token: str
    @param refresh_token: Refresh-токен полученный из Cookie.
    @type redis_client: RedisClient
    @param redis_client: Клиент Redis через Depends.
    @type user_agent: str
    @param user_agent: User-Agent из заголовка через Depends.

    @rtype: TokenPayload
    @return: Payload refresh-токена.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing token: {TokenType.refresh.name}",
        )

    refresh_token_payload = Tokenizer.decode_token(token=refresh_token)
    refresh_token_from_redis = await redis_client.get(
        key=Tokenizer.token_key_template.format(
            user_id=refresh_token_payload.sub,
            user_agent=refresh_token_payload.user_agent,
            token_type=TokenType.refresh.name,
        )
    )

    is_correct_token = refresh_token_from_redis == refresh_token
    is_correct_user_agent = user_agent == refresh_token_payload.user_agent
    if not is_correct_token or not is_correct_user_agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token, please login again",
        )

    return refresh_token_payload
