from models.mixin import PasswordCheckerMixin
from pydantic import BaseModel, EmailStr, Field, SecretStr


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
