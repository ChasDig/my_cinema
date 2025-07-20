from pydantic import BaseModel


class TokenPayload(BaseModel):
    type: str
    iat: float
    exp: float
    sub: str
    user_agent: str


class TokenInfo(BaseModel):
    type: str
    ttl: int
    token: str


class Tokens(BaseModel):
    access_token: TokenInfo
    refresh_token: TokenInfo
