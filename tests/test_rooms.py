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
    def test_list_rooms_without_token(
        self, http: requests.Session, api_url: str
    ) -> None:
        response = http.get(f"{api_url}/rooms")

        assert response.status_code == 401

    def test_public_room_visible_to_other_user(
        self,
        http: requests.Session,
        api_url: str,
        auth_headers: dict[str, str],
        other_auth_headers: dict[str, str],
    ) -> None:
        create_response = http.post(
            f"{api_url}/rooms", json=_room_payload(), headers=auth_headers
        )
        room_id = create_response.json()["id"]

        response = http.get(f"{api_url}/rooms", headers=other_auth_headers)

        assert response.status_code == 200, response.text
        room_ids = [room["id"] for room in response.json()]
        assert room_id in room_ids

    def test_public_room_is_member_false_for_non_member(
        self,
        http: requests.Session,
        api_url: str,
        auth_headers: dict[str, str],
        other_auth_headers: dict[str, str],
    ) -> None:
        create_response = http.post(
            f"{api_url}/rooms", json=_room_payload(), headers=auth_headers
        )
        room_id = create_response.json()["id"]

        response = http.get(f"{api_url}/rooms", headers=other_auth_headers)

        room_ids = {room["id"]: room for room in response.json()}
        assert room_ids[room_id]["is_member"] is False

    def test_private_room_hidden_from_non_member(
        self,
        http: requests.Session,
        api_url: str,
        auth_headers: dict[str, str],
        other_auth_headers: dict[str, str],
    ) -> None:
        create_response = http.post(
            f"{api_url}/rooms",
            json=_room_payload(is_private=True),
            headers=auth_headers,
        )
        room_id = create_response.json()["id"]

        response = http.get(f"{api_url}/rooms", headers=other_auth_headers)

        room_ids = [room["id"] for room in response.json()]
        assert room_id not in room_ids

    def test_private_room_visible_to_creator(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        create_response = http.post(
            f"{api_url}/rooms",
            json=_room_payload(is_private=True),
            headers=auth_headers,
        )
        room_id = create_response.json()["id"]

        response = http.get(f"{api_url}/rooms", headers=auth_headers)

        room_ids = {room["id"]: room for room in response.json()}
        assert room_id in room_ids
        assert room_ids[room_id]["is_member"] is True

    def test_list_rooms_respects_limit(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        for _ in range(3):
            http.post(f"{api_url}/rooms", json=_room_payload(), headers=auth_headers)

        response = http.get(
            f"{api_url}/rooms", params={"limit": 2}, headers=auth_headers
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) <= 2

    def test_list_rooms_invalid_limit_rejected(
        self, http: requests.Session, api_url: str, auth_headers: dict[str, str]
    ) -> None:
        response = http.get(
            f"{api_url}/rooms", params={"limit": 0}, headers=auth_headers
        )

        assert response.status_code == 422
