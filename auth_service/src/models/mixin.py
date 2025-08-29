from pydantic import SecretStr, field_validator
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
