"""Integration tests for GET /api/internships/suggestions with real database."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import User, UserRole
from tests.factories import create_test_user


def _setup_org(db: Session, name: str = "Test Org", approved: bool = True) -> User:
    """Create organization user with profile."""
    user = create_test_user(
        db,
        email=f"org_{datetime.now().timestamp()}_{name.lower().replace(' ', '_')}@test.edu",
        role=UserRole.ORGANIZATION,
    )
    prof = OrganizationProfile(
        user_id=user.id,
        organization_name=name,
        approval_status=ApprovalStatus.APPROVED if approved else ApprovalStatus.PENDING,
    )
    db.add(prof)
    db.commit()
    return user


def _create_posting(
    db: Session,
    org_id: int,
    title: str,
    skills_text: str,
    work_mode: InternshipWorkMode = InternshipWorkMode.REMOTE,
    location: str = "Addis Ababa",
    status: InternshipStatus = InternshipStatus.OPEN,
    days_future: int = 14,
) -> Internship:
    """Create internship posting."""
    deadline = datetime.now(UTC) + timedelta(days=days_future)
    posting = Internship(
        organization_id=org_id,
        title=title,
        description=f"Description for {title}. {skills_text}",
        requirements=f"Required skills: {skills_text}",
        work_mode=work_mode,
        location=location,
        status=status,
        application_deadline=deadline,
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting


def test_suggestions_no_skills_returns_empty_with_reason(real_db_client: TestClient) -> None:
    """Student with no skills receives empty list and NO_SKILLS reason_code."""
    resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "noskills@test.edu",
            "password": "Password123!",
            "full_name": "No Skills Student",
            "role": "student",
        },
    )
    assert resp.status_code == 201

    s_resp = real_db_client.get("/api/internships/suggestions")
    assert s_resp.status_code == 200
    data = s_resp.json()
    assert data["items"] == []
    assert data["reason_code"] == "NO_SKILLS"


def test_suggestions_lifecycle_exclusions_and_thresholds(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Only open, future-deadline, approved org, unapplied, >=30 score postings are suggested."""
    approved_org = _setup_org(real_db_session, "Approved Corp", approved=True)
    pending_org = _setup_org(real_db_session, "Pending Corp", approved=False)

    p_valid = _create_posting(
        real_db_session, approved_org.id, "Python Dev", "Python, FastAPI", days_future=10
    )
    _create_posting(
        real_db_session,
        approved_org.id,
        "Closed Dev",
        "Python, FastAPI",
        status=InternshipStatus.CLOSED,
    )
    _create_posting(
        real_db_session,
        approved_org.id,
        "Draft Dev",
        "Python, FastAPI",
        status=InternshipStatus.DRAFT,
    )
    _create_posting(
        real_db_session,
        approved_org.id,
        "Expired Dev",
        "Python, FastAPI",
        days_future=-2,
    )
    _create_posting(
        real_db_session,
        pending_org.id,
        "Pending Org Dev",
        "Python, FastAPI",
    )
    _create_posting(
        real_db_session,
        approved_org.id,
        "Unrelated Dev",
        "Ruby on Rails only",
    )

    reg_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "lifecycle_student@test.edu",
            "password": "Password123!",
            "full_name": "Lifecycle Student",
            "role": "student",
        },
    )
    assert reg_resp.status_code == 201
    stud_id = reg_resp.json()["id"]

    real_db_client.put(
        "/api/students/me",
        json={"skills": ["Python", "FastAPI"], "preferred_work_modes": ["remote"]},
    )

    res = real_db_client.get("/api/internships/suggestions")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == p_valid.id
    assert items[0]["score"] == (2 * 12) + 20 + 20  # 64
    assert items[0]["reasons"]["matched_skills"] == ["Python", "FastAPI"]
    assert items[0]["reasons"]["work_mode_match"] is True
    assert items[0]["reasons"]["location_match"] is True

    # Already-applied exclusion check
    app = Application(
        student_id=stud_id,
        posting_id=p_valid.id,
        cover_letter="Interested in Python",
        status=ApplicationStatus.SUBMITTED,
    )
    real_db_session.add(app)
    real_db_session.commit()

    res_applied = real_db_client.get("/api/internships/suggestions")
    assert res_applied.status_code == 200
    assert res_applied.json()["items"] == []


def test_suggestions_ordering_ties_and_query_bound(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Sort by score desc, then deadline asc, then id, with bounded query count."""
    org = _setup_org(real_db_session, "Tie Org", approved=True)

    # p1: 1 skill (12) + 10 neutral wm + 10 neutral loc = 32 score, deadline +5 days
    _create_posting(
        real_db_session,
        org.id,
        "Junior Python",
        "Python",
        work_mode=InternshipWorkMode.ONSITE,
        location="Gondar",
        days_future=5,
    )
    # p2: 2 skills (24) + 10 neutral wm + 10 neutral loc = 44 score, deadline +10 days
    p2 = _create_posting(
        real_db_session,
        org.id,
        "Mid Python",
        "Python, SQL",
        work_mode=InternshipWorkMode.ONSITE,
        location="Gondar",
        days_future=10,
    )
    # p3: 2 skills (24) + 10 wm + 10 loc = 44 score, deadline +3 days (earlier deadline)
    p3 = _create_posting(
        real_db_session,
        org.id,
        "Urgent Mid Python",
        "Python, SQL",
        work_mode=InternshipWorkMode.ONSITE,
        location="Gondar",
        days_future=3,
    )

    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "tie_student@test.edu",
            "password": "Password123!",
            "full_name": "Tie Student",
            "role": "student",
        },
    )
    real_db_client.put(
        "/api/students/me",
        json={"skills": ["Python", "SQL"]},
    )

    query_count = 0

    def _query_listener(*_args, **_kwargs):
        nonlocal query_count
        query_count += 1

    engine = real_db_session.get_bind()
    event.listen(engine, "before_cursor_execute", _query_listener)

    try:
        resp = real_db_client.get("/api/internships/suggestions?limit=2")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 2
        # Highest score with earlier deadline first: p3 (44, +3d), then p2 (44, +10d)
        assert items[0]["id"] == p3.id
        assert items[1]["id"] == p2.id
        # Bounded query count
        assert query_count <= 8, f"Expected <= 8 queries, observed {query_count}"
    finally:
        event.remove(engine, "before_cursor_execute", _query_listener)
