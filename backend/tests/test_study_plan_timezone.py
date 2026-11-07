"""Tests for study plan local timezone day bucketing and offset validation."""

from datetime import UTC, datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import UserRole
from app.services.study_plan import generate_study_plan
from tests.factories import create_test_user, login_test_user


def test_study_plan_timezone_bucketing_at_midnight_boundaries(
    real_db_session: Session,
) -> None:
    """Offset +180 shifts 00:30 local deadline to next day compared to UTC."""
    student = create_test_user(
        db=real_db_session, email="stu_tz_bounds@example.com", role=UserRole.STUDENT
    )
    instructor = create_test_user(
        db=real_db_session, email="inst_tz_bounds@example.com", role=UserRole.INSTRUCTOR
    )
    org_user = create_test_user(
        db=real_db_session, email="org_tz_bounds@example.com", role=UserRole.ORGANIZATION
    )
    real_db_session.add(
        OrganizationProfile(
            user_id=org_user.id,
            organization_name="Boundary Systems",
            approval_status=ApprovalStatus.APPROVED,
        )
    )
    course = Course(
        instructor_id=instructor.id,
        title="Distributed Systems",
        description="Time synchronization and consensus",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(student_id=student.id, course_id=course.id))

    # Base reference instant: 12:00 UTC (15:00 in UTC+3 on 2026-11-08)
    ref_time = datetime(2026, 11, 8, 12, 0, 0, tzinfo=UTC)
    offset_3h = timezone(timedelta(hours=3))

    # 1. Deadline at 23:30 local time today (2026-11-08 23:30+03:00 == 20:30 UTC)
    due_2330_local = datetime(2026, 11, 8, 23, 30, 0, tzinfo=offset_3h)
    due_2330_utc = due_2330_local.astimezone(UTC)

    # 2. Deadline at 00:30 local time tomorrow (2026-11-09 00:30+03:00 == 2026-11-08 21:30 UTC)
    due_0030_local = datetime(2026, 11, 9, 0, 30, 0, tzinfo=offset_3h)
    due_0030_utc = due_0030_local.astimezone(UTC)

    # Add open internship postings matching these boundary deadlines
    int_2330 = Internship(
        organization_id=org_user.id,
        title="Internship Due 23:30",
        description="Deadline at 23:30 local",
        requirements="Python",
        location="Remote",
        work_mode="remote",
        status=InternshipStatus.OPEN,
        application_deadline=due_2330_utc,
    )
    int_0030 = Internship(
        organization_id=org_user.id,
        title="Internship Due 00:30",
        description="Deadline at 00:30 local next day",
        requirements="Python",
        location="Remote",
        work_mode="remote",
        status=InternshipStatus.OPEN,
        application_deadline=due_0030_utc,
    )
    # Add assignment due at 00:30 on day 2 (2026-11-10 00:30 local == 2026-11-09 21:30 UTC)
    due_d2_local = datetime(2026, 11, 10, 0, 30, 0, tzinfo=offset_3h)
    a_d2 = Assignment(
        course_id=course.id,
        title="Assignment Due 00:30 Local Day 2",
        description="Prepares on day 1 with +180 offset, on day 0 with UTC",
        due_at=due_d2_local.astimezone(UTC),
        max_points=20,
    )
    real_db_session.add_all([int_2330, int_0030, a_d2])
    real_db_session.commit()

    # Plan WITH UTC+3 offset (+180 minutes)
    plan_local = generate_study_plan(
        db=real_db_session,
        student=student,
        days=7,
        current_time=ref_time,
        utc_offset_minutes=180,
    )

    day_0_items = plan_local.plan[0].items
    day_1_items = plan_local.plan[1].items

    # 23:30 deadline lands on day 0 (2026-11-08)
    assert any("Internship Due 23:30" in it.title for it in day_0_items)
    # 00:30 deadline lands on day 1 (2026-11-09)
    assert any("Internship Due 00:30" in it.title for it in day_1_items)
    assert not any("Internship Due 00:30" in it.title for it in day_0_items)
    # Assignment due 00:30 local day 2 prepares on day 1 (the day before its local deadline)
    assert any("Assignment Due 00:30 Local Day 2" in it.title for it in day_1_items)

    # In contrast, without offset (UTC 0): both internships share UTC date 2026-11-08
    plan_utc = generate_study_plan(
        db=real_db_session,
        student=student,
        days=7,
        current_time=ref_time,
        utc_offset_minutes=0,
    )
    utc_day_0_items = plan_utc.plan[0].items
    # In UTC, 21:30 is still 2026-11-08, so both fall on day 0
    assert any("Internship Due 23:30" in it.title for it in utc_day_0_items)
    assert any("Internship Due 00:30" in it.title for it in utc_day_0_items)


def test_study_plan_utc_offset_endpoint_validation(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """utc_offset_minutes query parameter is validated against [-720, 840]."""
    create_test_user(db=real_db_session, email="stu_tz_val@example.com", role=UserRole.STUDENT)
    login_test_user(real_db_client, "stu_tz_val@example.com")

    # Boundary valid offsets
    resp_min = real_db_client.get("/api/students/me/study-plan?utc_offset_minutes=-720")
    assert resp_min.status_code == 200

    resp_max = real_db_client.get("/api/students/me/study-plan?utc_offset_minutes=840")
    assert resp_max.status_code == 200

    resp_default = real_db_client.get("/api/students/me/study-plan?utc_offset_minutes=180")
    assert resp_default.status_code == 200

    # Invalid out-of-bounds offsets
    resp_under = real_db_client.get("/api/students/me/study-plan?utc_offset_minutes=-721")
    assert resp_under.status_code == 422

    resp_over = real_db_client.get("/api/students/me/study-plan?utc_offset_minutes=841")
    assert resp_over.status_code == 422
