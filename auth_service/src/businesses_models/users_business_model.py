from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from models.pg_models import Users
from models.api_models import RequestUserRegistration
from utils.custom_exception import (
    UserAlreadyExistsError,
    SQLAlchemyErrorCommit,
)


class UsersBusinessModel:

    def __init__(self, pg_session: AsyncSession) -> None:
        self._pg_session = pg_session

    async def registration_user(
        self,
        registration_data: RequestUserRegistration,
    ):
        existed_user = await self._check_user_by_exist(
            email=registration_data.email,
            nickname=registration_data.nickname,
        )

        if existed_user:
            raise UserAlreadyExistsError()

        try:
            self._pg_session.add(self._create_new_user(data=registration_data))
            await self._pg_session.commit()

        except SQLAlchemyError as ex:
            logger.error(
                f"Error create User(nickname={registration_data.nickname}, "
                f"email='{registration_data.email}'): {ex}"
            )
            await self._pg_session.rollback()

            raise SQLAlchemyErrorCommit(details=f"Error create user")

    async def _check_user_by_exist(
        self,
        email: EmailStr | str,
        nickname: str,
    ) -> Users | None:
        query = await self._pg_session.execute(
            select(
                Users,
            )
            .where(
                or_(
                    Users.nickname == nickname,
                    Users.email == email,
                )
            )
        )
        found_user = query.scalar_one_or_none()

        return found_user

    @staticmethod
    def _create_new_user(data: RequestUserRegistration) -> Users:
        return Users(
            nickname=data.nickname,
            email=data.email,
            password=data.password.get_secret_value(),
            first_name=data.first_name,
            last_name=data.last_name,
        )
