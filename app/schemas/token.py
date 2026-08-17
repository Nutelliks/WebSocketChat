from pydantic import BaseModel


class Token(BaseModel):
    token: str
    type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int
    type: str
