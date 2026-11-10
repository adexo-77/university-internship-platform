"""Tests for the Internship and Application detail access matrix across roles.

Policy:
- Internship details: students (open postings), owning org, coordinators, admin.
- Application details: applicant student, owning org, coordinators, admin.
- Instructors have no access to internships or applications.
Asserts status codes (200, 401, 403, 404) and no data leaks on refusal.
"""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.clock import get_now
from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def _seed_internship_data(db: Session) -> dict:
    now = get_now()
    stud_applicant = create_test_user(db, "app_stud@matrix.edu", UserRole.STUDENT)
    stud_other = create_test_user(db, "other_stud@matrix.edu", UserRole.STUDENT)
    inst_owner = create_test_user(db, "inst_owner@matrix.edu", UserRole.INSTRUCTOR)
    org_owner = create_test_user(db, "org_owner@matrix.edu", UserRole.ORGANIZATION)
    org_other = create_test_user(db, "org_other@matrix.edu", UserRole.ORGANIZATION)
    coord = create_test_user(db, "coord@matrix.edu", UserRole.COORDINATOR)
    admin = create_test_user(db, "admin@matrix.edu", UserRole.ADMIN)

    for org in (org_owner, org_other):
        db.add(
            OrganizationProfile(
                user_id=org.id,
                organization_name=f"Org {org.id}",
                approval_status=ApprovalStatus.APPROVED,
            )
        )

    internship = Internship(
        organization_id=org_owner.id,
        title="Software Intern",
        description="Backend Python dev",
        requirements="Python 3",
        location="Addis Ababa",
        work_mode=InternshipWorkMode.REMOTE,
        duration_weeks=12,
        application_deadline=now + timedelta(days=14),
        status=InternshipStatus.OPEN,
    )
    db.add(internship)
    db.flush()

    application = Application(
        posting_id=internship.id,
        student_id=stud_applicant.id,
        cover_letter="Passionate about Python development",
        status=ApplicationStatus.SUBMITTED,
    )
    db.add(application)
    db.commit()

    return {
        "stud_applicant": stud_applicant,
        "stud_other": stud_other,
        "inst_owner": inst_owner,
        "org_owner": org_owner,
        "org_other": org_other,
        "coord": coord,
        "admin": admin,
        "internship": internship,
        "application": application,
    }


def _check_leak(resp, terms: list[str]) -> None:
    if resp.status_code in (401, 403, 404):
        body = resp.text.lower()
        for term in terms:
            assert term.lower() not in body, f"Leaked '{term}' in {resp.status_code}"


def test_internship_detail_access_matrix(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Internship detail endpoint enforces strict role boundaries and privacy."""
    data = _seed_internship_data(real_db_session)
    iid = data["internship"].id
    terms = ["Backend Python dev"]

    matrix = {
        None: 401,
        "stud_applicant": 200,
        "stud_other": 200,
        "inst_owner": 404,  # Instructors have no access
        "org_owner": 200,
        "org_other": 404,
        "coord": 200,
        "admin": 200,
    }

    for user_key, expected in matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/internships/{iid}")
        assert r.status_code == expected, f"Internship mismatch for {user_key}"
        _check_leak(r, terms)


def test_application_detail_and_roster_access_matrix(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Application detail and applicant roster enforce isolation."""
    data = _seed_internship_data(real_db_session)
    iid = data["internship"].id
    appid = data["application"].id
    terms = ["Passionate about Python development"]

    app_matrix = {
        None: 401,
        "stud_applicant": 200,
        "stud_other": 404,
        "inst_owner": 404,
        "org_owner": 200,
        "org_other": 404,
        "coord": 200,
        "admin": 200,
    }
    roster_matrix = {
        None: 401,
        "stud_applicant": 403,
        "stud_other": 403,
        "inst_owner": 403,
        "org_owner": 200,
        "org_other": 404,
        "coord": 200,
        "admin": 200,
    }

    for user_key, expected in app_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/applications/{appid}")
        assert r.status_code == expected, f"Application detail mismatch for {user_key}"
        _check_leak(r, terms)

    for user_key, expected in roster_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/internships/{iid}/applications")
        assert r.status_code == expected, f"Applicants roster mismatch for {user_key}"
        _check_leak(r, terms)
