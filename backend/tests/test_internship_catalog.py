"""Tests for internship catalog visibility, search, filters, and detail access."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.internship import InternshipStatus, InternshipWorkMode
from app.models.organization_profile import OrganizationProfile
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_user,
    login_test_user,
)


def test_student_sees_only_open_postings(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_cat@test.com", UserRole.ORGANIZATION)
    p_open = create_test_internship(
        real_db_session, org, title="Open Posting", status=InternshipStatus.OPEN
    )
    create_test_internship(
        real_db_session, org, title="Draft Posting", status=InternshipStatus.DRAFT
    )
    create_test_internship(
        real_db_session, org, title="Closed Posting", status=InternshipStatus.CLOSED
    )

    student = create_test_user(real_db_session, "stud_cat@test.com", UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    resp = real_db_client.get("/api/internships")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == p_open.id


def test_admin_sees_all_postings_statuses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_adm@test.com", UserRole.ORGANIZATION)
    create_test_internship(real_db_session, org, title="Open 1", status=InternshipStatus.OPEN)
    create_test_internship(real_db_session, org, title="Draft 1", status=InternshipStatus.DRAFT)
    create_test_internship(real_db_session, org, title="Closed 1", status=InternshipStatus.CLOSED)

    admin = create_test_user(real_db_session, "admin_cat@test.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)

    resp = real_db_client.get("/api/internships")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3


def test_org_and_instructor_forbidden_from_catalogue(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_browse@test.com", UserRole.ORGANIZATION)
    login_test_user(real_db_client, org.email)
    assert real_db_client.get("/api/internships").status_code == 403

    instructor = create_test_user(real_db_session, "inst_browse@test.com", UserRole.INSTRUCTOR)
    login_test_user(real_db_client, instructor.email)
    assert real_db_client.get("/api/internships").status_code == 403


def test_student_sees_application_status_in_catalog(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_appflag@test.com", UserRole.ORGANIZATION)
    p1 = create_test_internship(real_db_session, org, title="Posting Applied")
    p2 = create_test_internship(real_db_session, org, title="Posting Not Applied")

    student = create_test_user(real_db_session, "stud_appflag@test.com", UserRole.STUDENT)
    create_test_application(real_db_session, p1, student)

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/internships")
    assert resp.status_code == 200
    items = {item["id"]: item for item in resp.json()["items"]}
    assert items[p1.id]["applied"] is True
    assert items[p1.id]["application_status"] == "submitted"
    assert items[p2.id]["applied"] is False
    assert items[p2.id]["application_status"] is None


def test_search_and_work_mode_filter_and_pagination(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(
        real_db_session, "org_search@test.com", UserRole.ORGANIZATION, full_name="Apex Corp"
    )
    prof = OrganizationProfile(user_id=org.id, organization_name="Apex Innovations")
    real_db_session.add(prof)
    real_db_session.commit()

    p_remote = create_test_internship(
        real_db_session, org, title="Frontend Dev", work_mode=InternshipWorkMode.REMOTE
    )
    create_test_internship(
        real_db_session, org, title="Backend Dev", work_mode=InternshipWorkMode.ONSITE
    )

    student = create_test_user(real_db_session, "stud_search@test.com", UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    # Search by title
    resp = real_db_client.get("/api/internships?q=Frontend")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["id"] == p_remote.id

    # Search by organization name
    resp = real_db_client.get("/api/internships?q=Apex")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    # Filter by work mode
    resp = real_db_client.get("/api/internships?work_mode=remote")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["work_mode"] == "remote"

    # Pagination
    resp = real_db_client.get("/api/internships?limit=1&offset=0")
    assert len(resp.json()["items"]) == 1
    assert resp.json()["total"] == 2


def test_internship_detail_access_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "owner_det@org.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "other_det@org.com", UserRole.ORGANIZATION)
    p_draft = create_test_internship(real_db_session, org1, status=InternshipStatus.DRAFT)
    p_open = create_test_internship(real_db_session, org1, status=InternshipStatus.OPEN)

    student = create_test_user(real_db_session, "stud_det@univ.edu", UserRole.STUDENT)
    admin = create_test_user(real_db_session, "admin_det@sys.gov", UserRole.ADMIN)

    # Student sees open posting (200), but draft gives 404
    login_test_user(real_db_client, student.email)
    assert real_db_client.get(f"/api/internships/{p_open.id}").status_code == 200
    assert real_db_client.get(f"/api/internships/{p_draft.id}").status_code == 404

    # Owner organization sees draft (200)
    login_test_user(real_db_client, org1.email)
    assert real_db_client.get(f"/api/internships/{p_draft.id}").status_code == 200

    # Other organization gets 404
    login_test_user(real_db_client, org2.email)
    assert real_db_client.get(f"/api/internships/{p_draft.id}").status_code == 404

    # Admin sees draft (200)
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get(f"/api/internships/{p_draft.id}").status_code == 200
