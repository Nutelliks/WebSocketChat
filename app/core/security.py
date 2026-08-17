from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings

_BCRYPT_MAX_BYTES = 72
_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > _BCRYPT_MAX_BYTES:
        raise ValueError("Пароль превышает максимальную длину bcrypt (72 байта)")

    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]

    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:
        return False


class TokenError(Exception):
    """Базовое исключение для ошибок валидации JWT."""


class TokenExpiredError(TokenError):
    """Токен истёк."""


class TokenInvalidError(TokenError):
    """Токен повреждён, подпись не совпадает или формат некорректен."""


def create_access_token(
    subject: str | UUID, expires_delta: timedelta | None = None
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Токен истёк") from exc
    except InvalidTokenError as exc:
        raise TokenInvalidError("Невалидный токен") from exc

    if payload.get("type") != "access":
        raise TokenInvalidError("Неверный тип токена")

    return payload