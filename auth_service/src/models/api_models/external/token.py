from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Модель данных - payload формируемого токена."""

    type: str
    iat: float
    exp: float
    sub: str
    user_agent: str


class TokenInfo(BaseModel):
    """Модель данных - token + meta-информация по нему."""

    type: str
    ttl: int
    token: str


class Tokens(BaseModel):
    """Модель данных - token-ы."""

    access_token: TokenInfo
    refresh_token: TokenInfo
