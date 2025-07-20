from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Body, Response, Depends, status

from database import get_pg_session, get_redis_client
from businesses_models import (
    UsersCreateBusinessModel,
    UsersLoginBusinessModel,
)
from database.redis_client import RedisClient
from depends import get_user_agent
from models.api_models import (
    RequestUserRegistration,
    RequestUserLoginData,
    Tokens,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
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
    business_model = UsersCreateBusinessModel(pg_session=pg_session)
    await business_model.registration_user(registration_data)

    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f"User '{registration_data.nickname}' was created",
    )

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Tokens,
)
async def login(
    login_data: Annotated[
        RequestUserLoginData,
        Body(),
    ],
    user_agent: str = Depends(get_user_agent),
    pg_session: AsyncSession = Depends(get_pg_session),
    redis_client: RedisClient = Depends(get_redis_client),
):
    business_model = UsersLoginBusinessModel(
        pg_session=pg_session,
        redis_client=redis_client,
    )

    return await business_model.login_user(
        login_data=login_data,
        user_agent=user_agent,
    )
