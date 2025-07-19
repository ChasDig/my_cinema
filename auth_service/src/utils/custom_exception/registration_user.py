from fastapi import HTTPException, status


class UserAlreadyExistsError(HTTPException):

    def __init__(self, detail: str = "User already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
