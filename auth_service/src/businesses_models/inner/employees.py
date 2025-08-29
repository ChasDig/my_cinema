from core.app_config import crypto_config
from core.app_logger import logger
from models.api_models.inner import RequestEmployeesRegistration
from models.pg_models.inner import Employees
from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import Cryptor, Hasher
from utils.custom_exception import AlreadyExistsError, SQLAlchemyErrorCommit


class EmployeesCreateBusinessModel:
    """BusinessModel: создание сотрудника."""

    def __init__(self, pg_session: AsyncSession) -> None:
        self._pg_session = pg_session

    async def execute(
        self,
        registration_data: RequestEmployeesRegistration,
    ) -> Employees:
        """
        Точка входа в выполнение процесса - создание сотрудника.

        @type registration_data: RequestEmployeesRegistration
        @param registration_data:

        @rtype: Employees
        @return:
        """
        await self._check_employer_by_exist(
            email=registration_data.email,
            username=registration_data.username,
        )
        employer = self._create_new_employer(data=registration_data)

        try:
            self._pg_session.add(employer)
            await self._pg_session.commit()
            await self._pg_session.refresh(employer)

            return employer

        except SQLAlchemyError as ex:
            user_name = registration_data.user_name
            logger.error("Error create InUserName=" f"{user_name}: {ex}")
            await self._pg_session.rollback()

            raise SQLAlchemyErrorCommit(details="Error create in_user")

    async def _check_employer_by_exist(
        self,
        email: EmailStr | str,
        username: str,
    ) -> None:
        """
        Проверка существования сотрудника по email и nickname.

        @type email: EmailStr | str
        @param email:
        @type user_name: str
        @param user_name

        @rtype: None
        @return:
        """
        _, email_hash = self._get_emails_secrets(email=email)

        query = await self._pg_session.execute(
            select(
                Employees,
            ).where(
                or_(
                    Employees.username == username,
                    Employees.email_hash == email_hash,
                )
            )
        )
        if query.scalar_one_or_none():
            raise AlreadyExistsError(entity=Employees)

    def _create_new_employer(
        self,
        data: RequestEmployeesRegistration,
    ) -> Employees:
        """
        Создание нового сотрудника.

        @type data: RequestEmployeesRegistration
        @param data:

        @rtype employer: Employees
        @return employer:
        """
        email_enc, email_hash = self._get_emails_secrets(email=data.email)

        employer = Employees(
            username=data.username,
            email_enc=email_enc,
            email_hash=email_hash,
            password_hash=Hasher.gen_password_hash(
                password=data.password.get_secret_value()
            ),
            is_staff=data.is_staff,
            is_superuser=data.is_superuser,
        )
        return employer

    @staticmethod
    def _get_emails_secrets(email: str | EmailStr) -> tuple[str, str]:
        """
        Получение зашифрованного email + хэш.

        @type email: str | EmailStr
        @param email:

        @rtype: tuple[str, str]
        @return: Зашифрованный email, hash email-а.
        """
        email_enc = Cryptor.encrypt_str(
            str_=str(email),
            password=crypto_config.email_master_password,
        )
        email_hash = Hasher.hash_str(
            str_=str(email),
            password=crypto_config.email_master_password,
        )

        return email_enc, email_hash
