from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger, crypto_config
from database.redis_client import RedisClient
from utils import Cryptor, Hasher, Tokenizer
from models.pg_models import Users
from models.api_models import (
    RequestUserRegistration,
    RequestUserLoginData,
    Tokens,
)
from utils.custom_exception import (
    UserAlreadyExistsError,
    SQLAlchemyErrorCommit,
    UserLoginError,
)


class UsersCreateBusinessModel:

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
                f"Error create UserNickname={registration_data.nickname}: {ex}"
            )
            await self._pg_session.rollback()

            raise SQLAlchemyErrorCommit(details=f"Error create user")

    async def _check_user_by_exist(
        self,
        email: EmailStr | str,
        nickname: str,
    ) -> Users | None:
        _, email_hash = self._get_emails_secrets(email=email)

        query = await self._pg_session.execute(
            select(
                Users,
            )
            .where(
                or_(
                    Users.nickname == nickname,
                    Users.email_hash == email_hash,
                )
            )
        )
        found_user = query.scalar_one_or_none()

        return found_user

    def _create_new_user(self, data: RequestUserRegistration) -> Users:
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
        email_enc = Cryptor.encrypt_str(
            str_=str(email),
            password=crypto_config.email_master_password,
        )
        email_hash = Hasher.hash_str(
            str_=email_enc,
            password=crypto_config.email_master_password,
        )

        return email_enc, email_hash


class UsersLoginBusinessModel:

    def __init__(self, pg_session: AsyncSession, redis_client: RedisClient):
        self._pg_session = pg_session
        self._redis_client = redis_client

    async def login_user(
        self,
        login_data: RequestUserLoginData,
        user_agent: str,
    ) -> Tokens:
        user: Users = await self._get_user_by_email(email=login_data.email)
        await self._check_password_hash(
            incoming_password=login_data.password.get_secret_value(),
            user_hash_password=user.password_hash,
        )

        user_id = str(user.id)
        tokens = Tokenizer.gen_tokens(user_id=user_id, user_agent=user_agent)
        await self._redis_client.set(
            key=tokens.access_token.type,
            value=tokens.access_token.token,
            ex=tokens.access_token.exp,
        )
        await self._redis_client.set(
            key=tokens.refresh_token.type,
            value=tokens.refresh_token.token,
            ex=tokens.refresh_token.exp,
        )

        return tokens

    async def _get_user_by_email(self, email: str | EmailStr) -> Users | None:
        _, email_hash = self._get_emails_secrets(email=email)

        query = await self._pg_session.execute(
            select(
                Users,
            )
            .where(
                Users.email_hash == email_hash,
            )
        )
        found_user = query.scalar_one_or_none()

        if not found_user:
            raise UserLoginError()

        return found_user

    @staticmethod
    def _get_emails_secrets(email: str | EmailStr) -> tuple[str, str]:
        email_enc = Cryptor.encrypt_str(
            str_=str(email),
            password=crypto_config.email_master_password,
        )
        email_hash = Hasher.hash_str(
            str_=email_enc,
            password=crypto_config.email_master_password,
        )

        return email_enc, email_hash

    async def _check_password_hash( # TODO:
        self,
        incoming_password: str,
        user_hash_password: str,
    ) -> bool:
        pass
        # if not password_is_valid:
        #     raise UserLoginError()
