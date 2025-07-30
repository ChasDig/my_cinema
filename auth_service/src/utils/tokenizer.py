from datetime import datetime, UTC, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status

from core import crypto_config, logger
from models.enums import TokenType
from models.api_models import TokenPayload, TokenInfo, Tokens


class Tokenizer:
    """Utils - работа с токенами пользователя."""

    header = {"algorithm": crypto_config.token_algorithm, "type": "JWT"}
    token_key_template = "{user_id}.{user_agent}.{token_type}"

    @classmethod
    def gen_token(
        cls,
        type_: str,
        now_: datetime,
        exp_: float,
        sub: str,
        user_agent: str,
    ) -> str:
        """
        Генерация токена.

        @type type_: str
        @param type_: Тип токена.
        @type now_: datetime
        @param now_: Дата и время создания.
        @type exp_: float
        @param exp_: TTL timestamp.
        @type sub: str
        @param sub: ID Пользователя.
        @type user_agent: str
        @param user_agent:

        @rtype: str
        @return:
        """
        payload = TokenPayload(
            type=type_,
            iat=now_.timestamp(),
            exp=exp_,
            sub=sub,
            user_agent=user_agent,
        )
        return jwt.encode(
            claims=payload.model_dump(),
            key=crypto_config.token_secret,
            algorithm=crypto_config.token_algorithm,
            headers=cls.header,
        )

    @classmethod
    def gen_tokens(cls, user_id: str, user_agent: str) -> Tokens:
        """
        Генерация токенов.

        @type user_id: str
        @param user_id: ID Пользователя.
        @type user_agent: str
        @param user_agent:

        @rtype: Tokens
        @return:
        """
        now_ = datetime.now(UTC)
        access_exp = (
            now_ + timedelta(minutes=crypto_config.access_token_exp_min)
        ).timestamp()
        refresh_exp = (
            now_ + timedelta(days=crypto_config.refresh_token_exp_days)
        ).timestamp()

        return Tokens(
            access_token=TokenInfo(
                type=TokenType.access.name,
                ttl=int(access_exp - now_.timestamp()),
                token=cls.gen_token(
                    type_=TokenType.access.name,
                    now_=now_,
                    exp_=access_exp,
                    sub=user_id,
                    user_agent=user_agent,
                ),
            ),
            refresh_token=TokenInfo(
                type=TokenType.refresh.name,
                ttl=int(refresh_exp - now_.timestamp()),
                token=cls.gen_token(
                    type_=TokenType.refresh.name,
                    now_=now_,
                    exp_=refresh_exp,
                    sub=user_id,
                    user_agent=user_agent,
                ),
            ),
        )

    @staticmethod
    def decode_token(token: str) -> TokenPayload:
        """
        Получение данных из токена.

        @type token: str
        @param token:

        @rtype: TokenPayload
        @return:
        """
        try:
            token = jwt.decode(
                token=token,
                key = crypto_config.token_secret,
                algorithms=[crypto_config.token_algorithm],
            )
            return TokenPayload(
                type=token["type"],
                iat=token["iat"],
                exp=token["exp"],
                sub=token["sub"],
                user_agent=token["user_agent"],
            )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token, please login again",
            )

        except KeyError as ex:
            logger.error(f"Not valid token: {ex}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token, please login again",
            )