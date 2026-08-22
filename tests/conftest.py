import uuid
from collections.abc import Iterator

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
