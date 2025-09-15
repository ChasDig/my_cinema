from uuid import UUID

from models.api_models.external import Tokens
from models.mixin import PasswordCheckerMixin
from pydantic import BaseModel, EmailStr, Field, SecretStr


class RequestEmployeesRegistration(BaseModel, PasswordCheckerMixin):
    """Request модель данных - регистрация сотрудника."""

    username: str = Field(examples=["Dart Vader Employer"])
    email: EmailStr = Field(examples=["dart_vaider_employer@gmail.com"])
    password: SecretStr = Field(examples=["DartVaderEmployerPassword123!"])
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class ResponseEmployeesRegistration(BaseModel):
    """Response модель данных - регистрация сотрудника."""

    employer_id: UUID | str


class RequestEmployeesLoginData(BaseModel, PasswordCheckerMixin):
    """Request модель данных - авторизация сотрудника."""

    email: EmailStr = Field(examples=["dart_vaider_employer@gmail.com"])
    password: SecretStr = Field(examples=["DartVaderEmployerPassword123!"])


class ResponseEmployeesLoginData(BaseModel):
    """Response модель данных - авторизация сотрудника."""

    employer_id: UUID | str
    tokens: Tokens
