from typing import Annotated

from businesses_models.inner import (
    EmployeesCreateBusinessModel,
    EmployeesLoginBusinessModel,
)
from database import get_pg_session, get_redis_client
from database.redis_client import RedisClient
from fastapi import APIRouter, Body, Depends, Header, status
from models.api_models.inner import (
    RequestEmployeesLoginData,
    RequestEmployeesRegistration,
    ResponseEmployeesLoginData,
    ResponseEmployeesRegistration,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/inner/employees",
    tags=["Employees"],
)


@router.post(
    "/registration",
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    registration_data: Annotated[
        RequestEmployeesRegistration,
        Body(),
    ],
    pg_session: AsyncSession = Depends(get_pg_session),
) -> ResponseEmployeesRegistration:
    """
    Регистрация сотрудника.

    @type registration_data: Annotated[RequestEmployeesRegistration, Body()]
    @param registration_data:
    @type pg_session: AsyncSession
    @param pg_session:

    @rtype: ResponseEmployeesRegistration
    @return:
    """
    business_model = EmployeesCreateBusinessModel(pg_session=pg_session)
    employer = await business_model.execute(registration_data)

    return ResponseEmployeesRegistration(employer_id=employer.id)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    login_data: Annotated[
        RequestEmployeesLoginData,
        Body(),
    ],
    user_agent: Annotated[str, Header()],
    pg_session: AsyncSession = Depends(get_pg_session),
    redis_client: RedisClient = Depends(get_redis_client),
) -> ResponseEmployeesLoginData:
    """
    Авторизация сотрудника.
    Refresh-токен - добавляется в Cookies.
    Access-токен - возвращается в теле ответа.

    @type login_data: Annotated[RequestEmployeesLoginData, Body()]
    @param login_data:
    @type user_agent: str
    @param user_agent:
    @type pg_session: AsyncSession
    @param pg_session:
    @type redis_client: RedisClient
    @param redis_client:

    @rtype: ResponseEmployeesLoginData
    @return:
    """
    business_model = EmployeesLoginBusinessModel(
        pg_session=pg_session,
        redis_client=redis_client,
        user_agent=user_agent,
    )
    employer_id, tokens = await business_model.execute(login_data=login_data)

    response_data = ResponseEmployeesLoginData(
        employer_id=employer_id,
        tokens=tokens,
    )

    return response_data
