from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Body,
    Response,
    Depends,
    status,
    Cookie,
    HTTPException,
)

from database import get_pg_session, get_redis_client
from businesses_models import (
    UsersCreateBusinessModel,
    UsersLoginBusinessModel,
    UsersRefreshBusinessModel,
)
from database.redis_client import RedisClient
from depends import get_user_agent
from models.api_models import (
    RequestUserRegistration,
    RequestUserLoginData,
    Tokens, TokenInfo,
)
from models.enums import TokenType


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/registration",
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    registration_data: Annotated[
        RequestUserRegistration,
        Body(),
    ],
    pg_session: AsyncSession = Depends(get_pg_session),
) -> Response:
    """
    Регистрация пользователя.

    @type registration_data: Annotated[RequestUserRegistration, Body()]
    @param registration_data: Данные пользователя.
    @type pg_session: AsyncSession
    @param pg_session: Сессия с БД Postgres через Depends.

    @rtype: Response
    @return:
    """
    business_model = UsersCreateBusinessModel(pg_session=pg_session)
    await business_model.execute(registration_data)

    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f"User '{registration_data.nickname}' was created",
    )

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
)
async def login(
    login_data: Annotated[
        RequestUserLoginData,
        Body(),
    ],
    response: Response,
    user_agent: str = Depends(get_user_agent),
    pg_session: AsyncSession = Depends(get_pg_session),
    redis_client: RedisClient = Depends(get_redis_client),
) -> TokenInfo:
    """
    Авторизация пользователя.
    Refresh-токен - добавляется в Cookies.
    Access-токен - возвращается в теле ответа.

    @type login_data: Annotated[RequestUserLoginData, Body()]
    @param login_data: Данные авторизации.
    @type response: Response
    @param response:
    @type user_agent: str
    @param user_agent: User-Agent из заголовка через Depends.
    @type pg_session: AsyncSession
    @param pg_session: Сессия с БД Postgres через Depends.
    @type redis_client: RedisClient
    @param redis_client: Клиент Redis через Depends.

    @rtype: TokenInfo
    @return: Access-токен.
    """
    business_model = UsersLoginBusinessModel(
        pg_session=pg_session,
        redis_client=redis_client,
    )

    tokens = await business_model.execute(
        login_data=login_data,
        user_agent=user_agent,
    )
    response.set_cookie(
        key=TokenType.refresh.name,
        value=tokens.refresh_token.token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return tokens.access_token

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
)
async def login(
    response: Response,
    user_agent: str = Depends(get_user_agent),
    refresh_token: str = Cookie(None, alias="RefreshToken"),
    redis_client: RedisClient = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_session),
) -> TokenInfo:
    """
    Обновление токенов пользователя.
    Refresh-токен - добавляется в Cookies.
    Access-токен - возвращается в теле ответа.

    @type response: Response
    @param response:
    @type user_agent: str
    @param user_agent: User-Agent из заголовка через Depends.
    @type refresh_token: str
    @param refresh_token: Refresh-токен, полученный и Cookie.
    @type pg_session: AsyncSession
    @param pg_session: Сессия с БД Postgres через Depends.
    @type redis_client: RedisClient
    @param redis_client: Клиент Redis через Depends.

    @rtype: TokenInfo
    @return: Access-токен.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing RefreshToken",
        )

    business_model = UsersRefreshBusinessModel(
        redis_client=redis_client,
        pg_session=pg_session,
    )
    tokens: Tokens = await business_model.execute(
        refresh_token=refresh_token,
        user_agent=user_agent,
    )

    response.set_cookie(
        key=TokenType.refresh.name,
        value=tokens.refresh_token.token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return tokens.access_token
