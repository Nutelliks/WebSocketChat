import uuid

import requests


def _make_payload(**overrides: str) -> dict[str, str]:
    unique = uuid.uuid4().hex[:10]
    payload = {
        "username": f"user_{unique}",
        "email": f"email_{unique}@example.com",
        "password": "StrongPass123",
    }
    payload.update(overrides)
    return payload


class TestRegister:
    def test_register_success(self, http: requests.Session, api_url: str) -> None:
        payload = _make_payload()

        response = http.post(f"{api_url}/auth/register", json=payload)

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["username"] == payload["username"]
        assert body["email"] == payload["email"]
        assert "id" in body
        assert "created_at" in body
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_duplicate_username(
        self, http: requests.Session, api_url: str
    ) -> None:
        first = _make_payload()
        http.post(f"{api_url}/auth/register", json=first).raise_for_status()

        second = _make_payload(username=first["username"])
        response = http.post(f"{api_url}/auth/register", json=second)

        assert response.status_code == 409

    def test_register_duplicate_email(
        self, http: requests.Session, api_url: str
    ) -> None:
        first = _make_payload()
        http.post(f"{api_url}/auth/register", json=first)

        second = _make_payload(username=first["email"])
        response = http.post(f"{api_url}/auth/register", json=second)

        assert response.status_code == 409

    def test_register_invalid_email(self, http: requests.Session, api_url: str) -> None:
        payload = _make_payload(email="not-an-email")

        response = http.post(f"{api_url}/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_short_password(
        self, http: requests.Session, api_url: str
    ) -> None:
        payload = _make_payload(password="short1")

        response = http.post(f"{api_url}/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_password_without_digit(
        self, http: requests.Session, api_url: str
    ) -> None:
        payload = _make_payload(password="onlyletters")

        response = http.post(f"{api_url}/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_invalid_username_chars(
        self, http: requests.Session, api_url: str
    ) -> None:
        payload = _make_payload(username="invalid username!")

        response = http.post(f"{api_url}/auth/register", json=payload)

        assert response.status_code == 422


class TestLogin:
    def test_login_success(
        self, http: requests.Session, api_url: str, registered_user: dict[str, str]
    ) -> None:
        response = http.post(
            f"{api_url}/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str) and body["access_token"]

    def test_login_with_email(
        self, http: requests.Session, api_url: str, registered_user: dict[str, str]
    ) -> None:
        response = http.post(
            f"{api_url}/auth/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 200, response.text

    def test_login_wrong_password(
        self, http: requests.Session, api_url: str, registered_user: dict[str, str]
    ) -> None:
        response = http.post(
            f"{api_url}/auth/login",
            data={
                "username": registered_user["username"],
                "password": "totally-wrong-password",
            },
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(
        self, http: requests.Session, api_url: str, registered_user: dict[str, str]
    ) -> None:
        response = http.post(
            f"{api_url}/auth/login",
            data={"username": "no-such-user", "password": "whatever123"},
        )

        assert response.status_code == 401
