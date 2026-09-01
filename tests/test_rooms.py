import uuid

import requests


def _room_payload(**overrides: object) -> dict[str, object]:
    unique = uuid.uuid4().hex[:8]
    payload: dict[str, object] = {
        "name": f"room_{unique}",
        "is_private": False,
    }
    payload.update(overrides)
    return payload


class TestCreateRoom:
    def test_create_public_room_success(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        payload = _room_payload()

        response = http.post(f"{api_url}/rooms", json=payload, headers=auth_headers)

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["name"] == payload["name"]
        assert body["is_private"] is False
        assert body["is_member"] is True
        assert "id" in body
        assert "created_by_id" in body
        assert "created_at" in body

    def test_create_private_room_success(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        payload = _room_payload(is_private=True)

        response = http.post(f"{api_url}/rooms", json=payload, headers=auth_headers)

        assert response.status_code == 201, response.text
        assert response.json()["is_private"] is True

    def test_create_room_without_token(
        self, http: requests.Session, api_url: str
    ) -> None:
        response = http.post(f"{api_url}/rooms", json=_room_payload())

        assert response.status_code == 401

    def test_create_room_name_too_short(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        payload = _room_payload(name="ab")

        response = http.post(f"{api_url}/rooms", json=payload, headers=auth_headers)

        assert response.status_code == 422

    def test_create_room_sets_owner_as_creator(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        me = http.get(f"{api_url}/auth/me", headers=auth_headers).json()

        response = http.post(
            f"{api_url}/rooms", json=_room_payload(), headers=auth_headers
        )

        assert response.json()["created_by_id"] == me["id"]


class TestListRooms:
    pass
