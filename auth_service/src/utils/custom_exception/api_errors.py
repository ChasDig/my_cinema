from typing import Type

from fastapi import HTTPException, status
from models.pg_models import Base


class SQLAlchemyErrorCommit(HTTPException):

    def __init__(self, details: str = "Error data commit") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=details,
        )


class RedisError(HTTPException):

    def __init__(self, details: str = "Redis base error") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=details,
        )


class AlreadyExistsError(HTTPException):

    def __init__(
        self,
        detail: str = "Entity already exists",
        entity: Type[Base] | None = None,
    ) -> None:
        if entity:
            detail = f"{entity.model_name()} already exists"

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class NotFoundError(HTTPException):

    def __init__(
        self,
        detail: str = "Entity not found",
        entity: Type[Base] | None = None,
    ) -> None:
        if entity:
            detail = f"{entity.model_name()} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
