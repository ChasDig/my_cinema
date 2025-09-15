from core.app_config import crypto_config
from core.app_logger import logger
from database.redis_client import RedisClient
from models.api_models.external import Tokens
from models.api_models.inner import (
    RequestEmployeesLoginData,
    RequestEmployeesRegistration,
)
from models.pg_models.inner import Employees
from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import Cryptor, Hasher, Tokenizer
from utils.custom_exception import (
    AlreadyExistsError,
    NotFoundError,
    SQLAlchemyErrorCommit,
)
from utils.mixins import TokensRefreshMixin


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


class EmployeesLoginBusinessModel(TokensRefreshMixin):
    """BusinessModel: авторизация сотрудника."""

    def __init__(
        self,
        pg_session: AsyncSession,
        redis_client: RedisClient,
        user_agent: str,
    ):
        self._pg_session = pg_session
        self._redis_client = redis_client
        self._user_agent = user_agent

    async def execute(
        self,
        login_data: RequestEmployeesLoginData,
    ) -> tuple[str, Tokens]:
        """
        Точка входа в выполнение процесса - авторизация сотрудника.

        @type login_data: RequestUserLoginData
        @param login_data:

        @rtype: tuple[str, Tokens]
        @return:
        """
        employer = await self._get_employer_by_email(
            email=login_data.email,
        )
        if not employer:
            raise NotFoundError(entity=Employees)

        await self._check_password_by_hash(
            incoming_password=login_data.password.get_secret_value(),
            user_hash_password=employer.password_hash,
        )

        employer_id = str(employer.id)
        await self._delete_tokens(
            user_id=employer_id,
            redis_client=self._redis_client,
            user_agent=self._user_agent,
        )

        tokens = Tokenizer.gen_tokens(
            user_id=employer_id,
            user_agent=self._user_agent,
        )
        await self._insert_tokens(
            tokens=tokens,
            user_id=employer_id,
            redis_client=self._redis_client,
            user_agent=self._user_agent,
            user_email_hash=employer.email_hash,
        )

        return employer_id, tokens

    async def _get_employer_by_email(
        self,
        email: str | EmailStr,
    ) -> Employees | None:
        """
        Получение сотрудника по переданному email.

        @type email: str | EmailStr
        @param email:

        @rtype: Employees | None
        @return:
        """
        email_hash = Hasher.hash_str(
            str_=email,
            password=crypto_config.email_master_password,
        )

        query = await self._pg_session.execute(
            select(
                Employees,
            ).where(
                Employees.email_hash == email_hash,
            )
        )

        employer: Employees | None = query.scalar_one_or_none()
        return employer
