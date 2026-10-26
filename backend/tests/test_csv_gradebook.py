"""Tests for course gradebook CSV export: columns, calculations, authorization, and safety."""

import csv
import io
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_gradebook_csv_columns_calculations_and_bom(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify gradebook CSV headers, grades, counts, average percent, and UTF-8 BOM."""
    instructor = create_test_user(real_db_session, "gb_inst@example.com", UserRole.INSTRUCTOR)
    student1 = create_test_user(
        real_db_session, "gb_s1@example.com", UserRole.STUDENT, full_name="አበበ ከበደ"
    )
    student2 = create_test_user(
        real_db_session, "gb_s2@example.com", UserRole.STUDENT, full_name="Meron Hailu"
    )

    course = Course(
        instructor_id=instructor.id, title="Data Systems", status=CourseStatus.PUBLISHED
    )
    real_db_session.add(course)
    real_db_session.commit()

    real_db_session.add_all(
        [
            Enrollment(course_id=course.id, student_id=student1.id),
            Enrollment(course_id=course.id, student_id=student2.id),
        ]
    )

    due = datetime.now(UTC) + timedelta(days=3)
    a1 = Assignment(course_id=course.id, title="SQL Basics", due_at=due, max_points=100)
    a2 = Assignment(course_id=course.id, title="Indexing", due_at=due, max_points=50)
    real_db_session.add_all([a1, a2])
    real_db_session.commit()

    # student1: submitted both, a1=90/100, a2=40/50 -> avg = (90 + 80)/2 = 85.0%
    real_db_session.add(
        Submission(assignment_id=a1.id, student_id=student1.id, content="c1", grade=90)
    )
    real_db_session.add(
        Submission(assignment_id=a2.id, student_id=student1.id, content="c2", grade=40)
    )

    # student2: submitted a1 only, ungraded -> submitted=1, graded=0, avg=""
    real_db_session.add(
        Submission(assignment_id=a1.id, student_id=student2.id, content="c3", grade=None)
    )
    real_db_session.commit()

    login_test_user(real_db_client, instructor.email)
    resp = real_db_client.get(f"/api/courses/{course.id}/gradebook.csv")
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM
    assert resp.headers["content-type"].startswith("text/csv")
    assert resp.headers["cache-control"] == "no-store"
    assert (
        resp.headers["content-disposition"]
        == f'attachment; filename="course_{course.id}_gradebook.csv"'
    )

    text = resp.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(text)))
    assert reader[0] == [
        "Student Name",
        "Email",
        "SQL Basics",
        "Indexing",
        "Submitted Count",
        "Graded Count",
        "Average Percent",
    ]

    row_by_email = {row[1]: row for row in reader[1:]}
    assert "gb_s1@example.com" in row_by_email
    assert row_by_email["gb_s1@example.com"][0] == "አበበ ከበደ"
    assert row_by_email["gb_s1@example.com"][2] == "90"
    assert row_by_email["gb_s1@example.com"][3] == "40"
    assert row_by_email["gb_s1@example.com"][4] == "2"
    assert row_by_email["gb_s1@example.com"][5] == "2"
    assert row_by_email["gb_s1@example.com"][6] == "85.0%"

    assert row_by_email["gb_s2@example.com"][2] == ""
    assert row_by_email["gb_s2@example.com"][3] == ""
    assert row_by_email["gb_s2@example.com"][4] == "1"
    assert row_by_email["gb_s2@example.com"][5] == "0"
    assert row_by_email["gb_s2@example.com"][6] == ""


def test_gradebook_csv_formula_injection_defense(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify formula injection characters are safely escaped with an apostrophe."""
    instructor = create_test_user(real_db_session, "gb_safe_inst@example.com", UserRole.INSTRUCTOR)
    course = Course(instructor_id=instructor.id, title="Security", status=CourseStatus.PUBLISHED)
    real_db_session.add(course)
    real_db_session.commit()

    malicious_names = [
        "=cmd|' /C calc'!A0",
        "+123456789",
        "-500Bonus",
        "@evilchannel",
        "\ttabbed",
        "\rreturn",
    ]
    for idx, name in enumerate(malicious_names):
        student = create_test_user(
            real_db_session, f"malicious_{idx}@example.com", UserRole.STUDENT, full_name=name
        )
        real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    real_db_session.commit()

    login_test_user(real_db_client, instructor.email)
    resp = real_db_client.get(f"/api/courses/{course.id}/gradebook.csv")
    assert resp.status_code == 200

    text = resp.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(text)))
    names_in_csv = [row[0] for row in reader[1:]]

    for orig_name in malicious_names:
        expected = f"'{orig_name}"
        assert expected in names_in_csv, f"Expected escaped name '{expected}' in CSV output"


def test_gradebook_csv_authorization_and_empty_state(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify owner instructor and admin allowed, others blocked (403), 404, and empty state."""
    owner_inst = create_test_user(real_db_session, "gb_owner@example.com", UserRole.INSTRUCTOR)
    other_inst = create_test_user(real_db_session, "gb_other_inst@example.com", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "gb_admin@example.com", UserRole.ADMIN)
    coord = create_test_user(real_db_session, "gb_coord@example.com", UserRole.COORDINATOR)
    student = create_test_user(real_db_session, "gb_stu@example.com", UserRole.STUDENT)
    org = create_test_user(real_db_session, "gb_org@example.com", UserRole.ORGANIZATION)

    empty_course = Course(
        instructor_id=owner_inst.id, title="Empty Course", status=CourseStatus.PUBLISHED
    )
    real_db_session.add(empty_course)
    real_db_session.commit()

    # Owner instructor -> 200 with empty rows
    login_test_user(real_db_client, owner_inst.email)
    resp = real_db_client.get(f"/api/courses/{empty_course.id}/gradebook.csv")
    assert resp.status_code == 200
    text = resp.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(text)))
    assert len(reader) == 1
    assert reader[0] == [
        "Student Name",
        "Email",
        "Submitted Count",
        "Graded Count",
        "Average Percent",
    ]

    # Admin -> 200
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get(f"/api/courses/{empty_course.id}/gradebook.csv").status_code == 200

    # Other instructor, coordinator, student, organization -> 403
    for user in [other_inst, coord, student, org]:
        login_test_user(real_db_client, user.email)
        assert (
            real_db_client.get(f"/api/courses/{empty_course.id}/gradebook.csv").status_code == 403
        )

    # Non-existent course -> 404
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get("/api/courses/999999/gradebook.csv").status_code == 404
