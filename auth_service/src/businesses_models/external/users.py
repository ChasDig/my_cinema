from core.app_config import crypto_config
from core.app_logger import logger
from database.redis_client import RedisClient
from models.api_models.external import (
    RequestUserLoginData,
    RequestUserRegistration,
    TokenPayload,
    Tokens,
)
from models.pg_models.external import Users
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


class UsersCreateBusinessModel:
    """BusinessModel: создание пользователя."""

    def __init__(self, pg_session: AsyncSession) -> None:
        self._pg_session = pg_session

    async def execute(
        self,
        registration_data: RequestUserRegistration,
    ) -> None:
        """
        Точка входа в выполнение процесса - создание пользователя.

        @type registration_data: RequestUserRegistration
        @param registration_data: Данные пользователя для регистрации.

        @rtype: None
        @return:
        """
        await self._check_user_by_exist(
            email=registration_data.email,
            nickname=registration_data.nickname,
        )

        try:
            self._pg_session.add(self._create_new_user(data=registration_data))
            await self._pg_session.commit()

        except SQLAlchemyError as ex:
            logger.error(
                f"Error create UserNickname={registration_data.nickname}: {ex}"
            )
            await self._pg_session.rollback()

            raise SQLAlchemyErrorCommit(details="Error create user")

    async def _check_user_by_exist(
        self,
        email: EmailStr | str,
        nickname: str,
    ) -> None:
        """
        Проверка существования пользователя по email и nickname.

        @type email: EmailStr | str
        @param email:
        @type nickname: str
        @param nickname

        @rtype: None
        @return:
        """
        _, email_hash = self._get_emails_secrets(email=email)

        query = await self._pg_session.execute(
            select(
                Users,
            ).where(
                or_(
                    Users.nickname == nickname,
                    Users.email_hash == email_hash,
                )
            )
        )
        if query.scalar_one_or_none():
            raise AlreadyExistsError(entity=Users)

    def _create_new_user(self, data: RequestUserRegistration) -> Users:
        """
        Создание нового пользователя.

        @type data: RequestUserRegistration
        @param data: Данные, полученные из запроса для создания пользователя.

        @rtype user: Users
        @return user:
        """
        email_enc, email_hash = self._get_emails_secrets(email=data.email)
        password_hash = Hasher.gen_password_hash(
            password=data.password.get_secret_value()
        )

        user = Users(
            nickname=data.nickname,
            email_enc=email_enc,
            email_hash=email_hash,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return user

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


class UsersLoginBusinessModel(TokensRefreshMixin):
    """BusinessModel: авторизация пользователя."""

    def __init__(
        self,
        pg_session: AsyncSession,
        redis_client: RedisClient,
        user_agent: str,
    ):
        self._pg_session = pg_session
        self._redis_client = redis_client
        self._user_agent = user_agent

    async def execute(self, login_data: RequestUserLoginData) -> Tokens:
        """
        Точка входа в выполнение процесса - авторизация пользователя.

        @type login_data: RequestUserLoginData
        @param login_data: Данные пользователя для авторизации.

        @rtype tokens: Tokens
        @return tokens: Access/Refresh токены.
        """
        user = await self._get_user_by_email(
            email=login_data.email,
        )
        if not user:
            raise NotFoundError(entity=Users)

        user_id = str(user.id)
        await self._check_password_by_hash(
            incoming_password=login_data.password.get_secret_value(),
            user_hash_password=user.password_hash,
        )
        await self._delete_tokens(
            user_id=user_id,
            redis_client=self._redis_client,
            user_agent=self._user_agent,
        )

        tokens = Tokenizer.gen_tokens(
            user_id=user_id,
            user_agent=self._user_agent,
        )
        await self._insert_tokens(
            tokens=tokens,
            user=user,
            redis_client=self._redis_client,
            user_agent=self._user_agent,
        )

        return tokens

    async def _get_user_by_email(self, email: str | EmailStr) -> Users | None:
        """
        Получение пользователя по переданному email.

        @type email: str | EmailStr
        @param email:

        @rtype: Users | None
        @return:
        """
        email_hash = Hasher.hash_str(
            str_=email,
            password=crypto_config.email_master_password,
        )

        query = await self._pg_session.execute(
            select(
                Users,
            ).where(
                Users.email_hash == email_hash,
            )
        )

        user: Users | None = query.scalar_one_or_none()
        return user

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


class UsersRefreshBusinessModel(TokensRefreshMixin):
    """BusinessModel: обновление токенов пользователя."""

    def __init__(self, pg_session: AsyncSession, redis_client: RedisClient):
        self._pg_session = pg_session
        self._redis_client = redis_client

    async def execute(self, refresh_token_payload: TokenPayload) -> Tokens:
        """
        Точка входа в выполнение процесса - обновление токенов пользователя.

        @type refresh_token_payload: TokenPayload
        @param refresh_token_payload:

        @rtype tokens: Tokens
        @return tokens: Access/Refresh токены.
        """
        user = await self._get_user_by_id(id_=refresh_token_payload.sub)
        if not user:
            raise NotFoundError(entity=Users)

        user_id = str(user.id)
        user_agent = refresh_token_payload.user_agent
        await self._delete_tokens(
            user_id=user_id,
            redis_client=self._redis_client,
            user_agent=user_agent,
        )

        tokens = Tokenizer.gen_tokens(user_id=user_id, user_agent=user_agent)
        await self._insert_tokens(
            tokens=tokens,
            user=user,
            redis_client=self._redis_client,
            user_agent=user_agent,
        )

        return tokens

    async def _get_user_by_id(self, id_: str) -> Users | None:
        """
        Получение пользователя по ID.

        @type id_: str
        @param id_:

        @rtype: Users | None
        @return:
        """
        query = await self._pg_session.execute(
            select(
                Users,
            ).where(
                Users.id == id_,
            )
        )

        user: Users | None = query.scalar_one_or_none()
        return user
