from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int
    type: str
