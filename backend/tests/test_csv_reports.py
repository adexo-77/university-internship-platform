"""Tests for applicants CSV and admin/coordinator reports: columns, permissions, and security."""

import csv
import io
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.student_profile import StudentProfile
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_applicants_csv_columns_and_authorization(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify applicants CSV headers, student details, access rules, and guards."""
    owner_org = create_test_user(real_db_session, "app_org@example.com", UserRole.ORGANIZATION)
    other_org = create_test_user(
        real_db_session, "app_other_org@example.com", UserRole.ORGANIZATION
    )
    admin = create_test_user(real_db_session, "app_admin@example.com", UserRole.ADMIN)
    coord = create_test_user(real_db_session, "app_coord@example.com", UserRole.COORDINATOR)
    student = create_test_user(
        real_db_session, "app_stu@example.com", UserRole.STUDENT, full_name="Abebe B"
    )
    inst = create_test_user(real_db_session, "app_inst@example.com", UserRole.INSTRUCTOR)

    prof = StudentProfile(
        user_id=student.id,
        university="Addis Ababa University",
        department="Software Eng",
        year_of_study=3,
        skills=["Python"],
    )
    real_db_session.add(prof)

    posting = Internship(
        organization_id=owner_org.id,
        title="Backend Engineer Intern",
        description="FastAPI dev",
        requirements="Python",
        location="Bole, Addis Ababa",
        work_mode=InternshipWorkMode.HYBRID,
        application_deadline=datetime.now(UTC) + timedelta(days=14),
        status=InternshipStatus.OPEN,
    )
    real_db_session.add(posting)
    real_db_session.commit()

    # Add application
    real_db_session.add(
        Application(
            posting_id=posting.id,
            student_id=student.id,
            cover_letter="My cover letter",
            status=ApplicationStatus.SHORTLISTED,
        )
    )
    real_db_session.commit()

    # Owner org -> 200
    login_test_user(real_db_client, owner_org.email)
    resp = real_db_client.get(f"/api/internships/{posting.id}/applicants.csv")
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")
    text = resp.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(text)))
    assert reader[0] == [
        "Applicant Name",
        "Email",
        "University",
        "Department",
        "Year of Study",
        "Status",
        "Applied Date",
    ]
    assert len(reader) == 2
    assert reader[1][0] == "Abebe B"
    assert reader[1][1] == "app_stu@example.com"
    assert reader[1][2] == "Addis Ababa University"
    assert reader[1][3] == "Software Eng"
    assert reader[1][4] == "3"
    assert reader[1][5] == "shortlisted"

    # Admin -> 200, Coordinator -> 200
    for u in [admin, coord]:
        login_test_user(real_db_client, u.email)
        assert (
            real_db_client.get(f"/api/internships/{posting.id}/applicants.csv").status_code == 200
        )

    # Other org, student, instructor -> 403
    for u in [other_org, student, inst]:
        login_test_user(real_db_client, u.email)
        assert (
            real_db_client.get(f"/api/internships/{posting.id}/applicants.csv").status_code == 403
        )

    # Non-existent -> 404
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get("/api/internships/999999/applicants.csv").status_code == 404


def test_applications_report_csv_and_role_access(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify applications report CSV content and role boundaries (admin and coordinator only)."""
    admin = create_test_user(real_db_session, "rep_admin@example.com", UserRole.ADMIN)
    coord = create_test_user(real_db_session, "rep_coord@example.com", UserRole.COORDINATOR)
    inst = create_test_user(real_db_session, "rep_inst@example.com", UserRole.INSTRUCTOR)
    stu = create_test_user(real_db_session, "rep_stu@example.com", UserRole.STUDENT)
    org = create_test_user(real_db_session, "rep_org@example.com", UserRole.ORGANIZATION)

    posting = Internship(
        organization_id=org.id,
        title="Frontend Intern",
        description="React dev",
        requirements="TypeScript",
        location="Remote",
        work_mode=InternshipWorkMode.REMOTE,
        application_deadline=datetime.now(UTC) + timedelta(days=7),
        status=InternshipStatus.OPEN,
    )
    real_db_session.add(posting)
    real_db_session.commit()

    real_db_session.add(
        Application(
            posting_id=posting.id,
            student_id=stu.id,
            cover_letter="Cover",
            status=ApplicationStatus.ACCEPTED,
            decided_at=datetime.now(UTC),
        )
    )
    real_db_session.commit()

    # Admin and coordinator -> 200
    for u in [admin, coord]:
        login_test_user(real_db_client, u.email)
        resp = real_db_client.get("/api/admin/reports/applications.csv")
        assert resp.status_code == 200
        text = resp.content.decode("utf-8-sig")
        reader = list(csv.reader(io.StringIO(text)))
        assert reader[0] == [
            "Posting",
            "Organization",
            "Applicant",
            "Status",
            "Applied Date",
            "Decided Date",
        ]
        assert len(reader) >= 2

    # Instructor, student, organization -> 403
    for u in [inst, stu, org]:
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/admin/reports/applications.csv").status_code == 403


def test_users_report_csv_admin_only_and_no_sensitive_leak(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify users report is admin-only and never leaks password hashes or session tokens."""
    admin = create_test_user(real_db_session, "user_rep_adm@example.com", UserRole.ADMIN)
    coord = create_test_user(real_db_session, "user_rep_coord@example.com", UserRole.COORDINATOR)
    inst = create_test_user(real_db_session, "user_rep_inst@example.com", UserRole.INSTRUCTOR)

    # Admin -> 200
    login_test_user(real_db_client, admin.email)
    resp = real_db_client.get("/api/admin/reports/users.csv")
    assert resp.status_code == 200

    text = resp.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(text)))
    assert reader[0] == ["ID", "Name", "Email", "Role", "Active", "Created Date"]

    # Verify no sensitive columns exist
    header_lower = [h.lower() for h in reader[0]]
    for sensitive in ["password", "hash", "salt", "token", "secret", "session"]:
        assert sensitive not in header_lower
        for row in reader:
            for cell in row:
                assert sensitive not in cell.lower(), (
                    f"Sensitive keyword '{sensitive}' found in cell '{cell}'"
                )

    # Coordinator, instructor, others -> 403 (admin only!)
    for u in [coord, inst]:
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/admin/reports/users.csv").status_code == 403
