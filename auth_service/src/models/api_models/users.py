from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from pydantic_core import PydanticCustomError


class PasswordCheckerMixin:
    """Mixin - проверка пароля."""

    @field_validator("password", mode="after")
    @classmethod
    def check_password(cls, value: SecretStr) -> SecretStr:
        """
        Валидация пароля пользователя.

        @type value: SecretStr
        @param value:

        @rtype: SecretStr
        @return:
        """
        if len(value.get_secret_value()) < 8:
            raise PydanticCustomError(
                "user-registration-error",
                "Not valid password: min len {min_len}",
                {"min_len": 8},
            )

        elif not any(s.isupper() for s in value.get_secret_value()):
            raise PydanticCustomError(
                "user-registration-error",
                "Not valid password: {error_msg}",
                {"error_msg": "nof found upper simbols"},
            )

        return value


class RequestUserRegistration(BaseModel, PasswordCheckerMixin):
    """Request модель данных - регистрация пользователя."""

    nickname: str = Field(examples=["Dart Vader"])
    email: EmailStr = Field(examples=["dart_vaider@gmail.com"])
    password: SecretStr = Field(examples=["DartVaderPassword123!"])

    first_name: str | None = Field(default=None, examples=["Dart"])
    last_name: str | None = Field(default=None, examples=["Vader"])


class RequestUserLoginData(BaseModel, PasswordCheckerMixin):
    """Request модель данных - авторизация пользователя."""

    email: EmailStr = Field(examples=["dart_vaider@gmail.com"])
    password: SecretStr = Field(examples=["DartVaderPassword123!"])
