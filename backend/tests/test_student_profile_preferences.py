"""Tests for student profile preferences (preferred_work_modes and preferred_location)."""

from fastapi.testclient import TestClient


def _register_student(client: TestClient, email: str = "prefs_student@test.edu") -> dict[str, str]:
    """Helper to register and authenticate a student user."""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Preference Student",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_student_profile_default_preferences(real_db_client: TestClient) -> None:
    """A newly registered student defaults to empty preferred_work_modes and None location."""
    user = _register_student(real_db_client, "new_prefs@test.edu")
    resp = real_db_client.get("/api/students/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user["id"]
    assert data["preferred_work_modes"] == []
    assert data["preferred_location"] is None


def test_student_profile_update_preferences_success(real_db_client: TestClient) -> None:
    """Updating preferred_work_modes and preferred_location saves and retrieves correctly."""
    _register_student(real_db_client, "update_prefs@test.edu")

    payload = {
        "preferred_work_modes": ["remote", "hybrid"],
        "preferred_location": "Addis Ababa",
    }
    put_resp = real_db_client.put("/api/students/me", json=payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["preferred_work_modes"] == ["remote", "hybrid"]
    assert data["preferred_location"] == "Addis Ababa"

    get_resp = real_db_client.get("/api/students/me")
    assert get_resp.status_code == 200
    assert get_resp.json()["preferred_work_modes"] == ["remote", "hybrid"]
    assert get_resp.json()["preferred_location"] == "Addis Ababa"


def test_student_profile_preferences_trim_and_deduplicate(real_db_client: TestClient) -> None:
    """Work modes are trimmed, lowercased, and deduplicated."""
    _register_student(real_db_client, "dedup_prefs@test.edu")

    payload = {
        "preferred_work_modes": ["  Remote ", "remote", "HYBRID", "onsite", "hybrid"],
        "preferred_location": "  Hawassa  ",
    }
    put_resp = real_db_client.put("/api/students/me", json=payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["preferred_work_modes"] == ["remote", "hybrid", "onsite"]
    assert data["preferred_location"] == "Hawassa"


def test_student_profile_invalid_work_mode_rejected(real_db_client: TestClient) -> None:
    """Unsupported work modes are rejected with 422."""
    _register_student(real_db_client, "invalid_mode@test.edu")

    payload = {"preferred_work_modes": ["freelance"]}
    put_resp = real_db_client.put("/api/students/me", json=payload)
    assert put_resp.status_code == 422


def test_student_profile_preferred_location_length_boundary(real_db_client: TestClient) -> None:
    """Preferred location accepts up to 80 characters and rejects 81 characters."""
    _register_student(real_db_client, "boundary_loc@test.edu")

    valid_payload = {"preferred_location": "A" * 80}
    put_resp = real_db_client.put("/api/students/me", json=valid_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["preferred_location"] == "A" * 80

    invalid_payload = {"preferred_location": "A" * 81}
    bad_resp = real_db_client.put("/api/students/me", json=invalid_payload)
    assert bad_resp.status_code == 422


def test_student_profile_preferred_location_control_chars_rejected(
    real_db_client: TestClient,
) -> None:
    """Control characters and null bytes in preferred_location trigger 422."""
    _register_student(real_db_client, "control_loc@test.edu")

    put_resp = real_db_client.put(
        "/api/students/me",
        json={"preferred_location": "Addis\x00Ababa"},
    )
    assert put_resp.status_code == 422

    put_resp2 = real_db_client.put(
        "/api/students/me",
        json={"preferred_location": "Addis\nAbaba"},
    )
    assert put_resp2.status_code == 422


def test_student_profile_blank_location_normalized_to_none(real_db_client: TestClient) -> None:
    """Empty or whitespace-only location normalizes to None."""
    _register_student(real_db_client, "blank_loc@test.edu")

    put_resp = real_db_client.put(
        "/api/students/me",
        json={"preferred_location": "   "},
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["preferred_location"] is None


def test_student_profile_extra_fields_forbidden(real_db_client: TestClient) -> None:
    """Extra unexpected payload fields are forbidden with 422."""
    _register_student(real_db_client, "extra_fields@test.edu")

    put_resp = real_db_client.put(
        "/api/students/me",
        json={"preferred_salary": 100000},
    )
    assert put_resp.status_code == 422
