"""Integration tests for course resource URL schemes, validation, limit, and ordering."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.course import Course, CourseStatus
from app.models.user import User, UserRole
from tests.factories import create_test_user, login_test_user


def _seed_course(
    db: Session, instructor: User, status: CourseStatus = CourseStatus.PUBLISHED
) -> Course:
    course = Course(
        instructor_id=instructor.id,
        title="Software Security",
        description="Core computing",
        status=status,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.mark.parametrize(
    "bad_url",
    [
        "javascript:alert('xss')",
        "JAVASCRIPT:alert(1)",
        "javascript://alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "DATA:text/plain;base64,SGVsbG8=",
        "ftp://files.example.com/test",
        "file:///etc/passwd",
        "mailto:user@example.com",
        "about:blank",
        "//example.com/path",
        "example.com/path",
        "http://",
        "https://",
    ],
)
def test_dangerous_url_schemes_rejected(
    real_db_client: TestClient, real_db_session: Session, bad_url: str
) -> None:
    """Dangerous and non-http(s) schemes are rejected with 422."""
    inst = create_test_user(
        real_db_session, f"inst_url_{abs(hash(bad_url))}@test.edu", UserRole.INSTRUCTOR
    )
    course = _seed_course(real_db_session, inst)
    login_test_user(real_db_client, inst.email)

    resp = real_db_client.post(
        f"/api/courses/{course.id}/resources",
        json={"title": "Resource", "url": bad_url},
    )
    assert resp.status_code == 422


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("url", "https://example.com/\x00evil"),
        ("url", "https://example.com/\x1fevil"),
        ("url", "https://example.com/\x07evil"),
        ("title", "Title\x00evil"),
        ("title", "Title\x1fevil"),
        ("title", "Title\x07evil"),
        ("description", "Desc\x00evil"),
        ("description", "Desc\x1fevil"),
        ("description", "Desc\x07evil"),
    ],
)
def test_null_bytes_and_control_chars_rejected(
    real_db_client: TestClient, real_db_session: Session, field: str, bad_value: str
) -> None:
    """Null bytes and control characters in any text field return 422."""
    inst = create_test_user(
        real_db_session, f"inst_ctl_{field}_{abs(hash(bad_value))}@test.edu", UserRole.INSTRUCTOR
    )
    course = _seed_course(real_db_session, inst)
    login_test_user(real_db_client, inst.email)

    payload = {"title": "Valid Title", "url": "https://example.com", "description": "Valid Desc"}
    payload[field] = bad_value

    resp = real_db_client.post(f"/api/courses/{course.id}/resources", json=payload)
    assert resp.status_code == 422


def test_field_bounds_and_extra_fields_forbidden(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Payload enforces length bounds and strictly forbids extra fields."""
    inst = create_test_user(real_db_session, "inst_bnd@test.edu", UserRole.INSTRUCTOR)
    course = _seed_course(real_db_session, inst)
    login_test_user(real_db_client, inst.email)

    # Empty title
    assert (
        real_db_client.post(
            f"/api/courses/{course.id}/resources",
            json={"title": "", "url": "https://example.com"},
        ).status_code
        == 422
    )

    # Title > 120 chars
    assert (
        real_db_client.post(
            f"/api/courses/{course.id}/resources",
            json={"title": "A" * 121, "url": "https://example.com"},
        ).status_code
        == 422
    )

    # URL > 500 chars
    assert (
        real_db_client.post(
            f"/api/courses/{course.id}/resources",
            json={"title": "Valid", "url": "https://example.com/" + ("a" * 490)},
        ).status_code
        == 422
    )

    # Description > 500 chars
    assert (
        real_db_client.post(
            f"/api/courses/{course.id}/resources",
            json={"title": "Valid", "url": "https://example.com", "description": "d" * 501},
        ).status_code
        == 422
    )

    # Extra fields forbidden
    resp_extra = real_db_client.post(
        f"/api/courses/{course.id}/resources",
        json={"title": "Valid", "url": "https://example.com", "unknown_field": "hacker"},
    )
    assert resp_extra.status_code == 422


def test_resource_limit_and_ordering(real_db_client: TestClient, real_db_session: Session) -> None:
    """At most 50 resources per course; 51st returns 409; results ordered by creation."""
    inst = create_test_user(real_db_session, "inst_lim@test.edu", UserRole.INSTRUCTOR)
    course = _seed_course(real_db_session, inst)
    login_test_user(real_db_client, inst.email)

    # Create 50 resources
    for i in range(1, 51):
        res = real_db_client.post(
            f"/api/courses/{course.id}/resources",
            json={"title": f"Resource {i:02d}", "url": f"https://example.com/{i}"},
        )
        assert res.status_code == 201

    # 51st resource fails with 409 RESOURCE_LIMIT_EXCEEDED
    res_overflow = real_db_client.post(
        f"/api/courses/{course.id}/resources",
        json={"title": "Resource 51", "url": "https://example.com/51"},
    )
    assert res_overflow.status_code == 409
    assert res_overflow.json()["code"] == "RESOURCE_LIMIT_EXCEEDED"

    # Check ordering: ordered by creation (1 through 50)
    list_res = real_db_client.get(f"/api/courses/{course.id}/resources")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 50
    assert items[0]["title"] == "Resource 01"
    assert items[49]["title"] == "Resource 50"
