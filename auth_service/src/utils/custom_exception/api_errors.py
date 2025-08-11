from fastapi import HTTPException, status


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
