from typing import Annotated

from fastapi import APIRouter, Body, Response, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.api_models import RequestUserRegistration
from businesses_models import UsersBusinessModel
from database import get_pg_session

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/registration",
    dependencies=[],  # TODO: validator
    status_code=status.HTTP_201_CREATED,
)
async def registration_users(
    registration_data: Annotated[
        RequestUserRegistration,
        Body(),
    ],
    pg_session: AsyncSession = Depends(get_pg_session),
) -> Response:
    business_model = UsersBusinessModel(pg_session=pg_session)
    await business_model.registration_user(registration_data)

    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f"User '{registration_data.nickname}' was created",
    )