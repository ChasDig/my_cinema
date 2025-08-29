from typing import Annotated

from businesses_models.inner import EmployeesCreateBusinessModel
from database import get_pg_session
from fastapi import APIRouter, Body, Depends, status
from models.api_models.inner import (
    RequestEmployeesRegistration,
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
