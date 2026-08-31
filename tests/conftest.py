import uuid
from collections.abc import Callable, Iterator

import pytest
import requests

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def api_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def http() -> Iterator[requests.Session]:
    with requests.Session() as session:
        yield session


@pytest.fixture
def user_payload() -> dict[str, str]:
    unique = uuid.uuid4().hex[:10]
    return {
        "username": f"user_{unique}",
        "email": f"email_{unique}@chat.com",
        "password": "StrongPass123",
    }


@pytest.fixture
def registered_user(
    http: requests.Session, api_url: str, user_payload: dict[str, str]
) -> dict[str, str]:
    response = http.post(f"{api_url}/auth/register", json=user_payload)
    assert response.status_code == 201, response.text
    return user_payload


@pytest.fixture
def auth_token(
    http: requests.Session, api_url: str, registered_user: dict[str, str]
) -> str:
    response = http.post(
        f"{api_url}/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def register_user(
    http: requests.Session, api_url: str
) -> Callable[..., dict[str, str]]:
    """Фабрика: позволяет зарегистрировать сколько угодно независимых
    пользователей в рамках одного теста (в отличие от registered_user,
    который кэшируется pytest один раз на тест)."""

    def _register(**overrides: str) -> dict[str, str]:
        unique = uuid.uuid4().hex[:10]
        payload = {
            "username": f"user_{unique}",
            "email": f"email_{unique}@chat.com",
            "password": "StrongPass123",
        }
        payload.update(overrides)
        response = http.post(f"{api_url}/auth/register", json=payload)
        assert response.status_code == 201, response.text
        return payload

    return _register


@pytest.fixture
def login_user(
    http: requests.Session,
    api_url: str,
) -> Callable[[dict[str, str]], str]:
    def _login(credentials: dict[str, str]) -> str:
        response = http.post(
            f"{api_url}/auth/login",
            data={
                "username": credentials["username"],
                "password": credentials["password"],
            },
        )
        assert response.status_code == 200, response.text
        return response.json()["access_token"]

    return _login


@pytest.fixture
def other_auth_headers(
    register_user: Callable[..., dict[str, str]], login_user: Callable[[dict[str, str]], str]
) -> dict[str, str]:
    """Готовые заголовки авторизации для ВТОРОГО, независимого пользователя —
    нужно для проверки видимости комнат между разными аккаунтами."""
    other_user = register_user()
    token = login_user(other_user)
    return {"Authorization": f"Bearer {token}"}
