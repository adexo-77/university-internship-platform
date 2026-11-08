"""Integration tests verifying study plan badge sentences match the badges API."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.services.badge import BADGE_DEFINITIONS
from tests.factories import create_test_student, login_test_user


def test_study_plan_nearest_badge_sentence_matches_badges_api_for_seeded_students(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Nearest badge sentence in study plan strictly equals GET /api/students/me/badges."""
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from seed_demo import seed_demo

    seed_demo(real_db_session, force=True)

    allowed_titles = {d["title"] for d in BADGE_DEFINITIONS}

    for email in [
        "abel.tesfaye@example.com",
        "meron.girma@example.com",
        "dawit.lemma@example.com",
    ]:
        login_test_user(real_db_client, email, "12345678")

        badges_resp = real_db_client.get("/api/students/me/badges")
        assert badges_resp.status_code == 200
        badges = badges_resp.json()

        # Compute nearest unearned countable badge from real badges API data
        unearned_countable = [
            b
            for b in badges
            if not b["earned"] and b.get("progress") and b["progress"].get("target")
        ]
        assert unearned_countable, f"Expected unearned countable badges for {email}"

        # Highest progress ratio
        nearest = max(
            unearned_countable,
            key=lambda b: (
                (b["progress"]["current"] or 0) / b["progress"]["target"],
                b["title"],
            ),
        )

        plan_resp = real_db_client.get("/api/students/me/study-plan?days=7")
        assert plan_resp.status_code == 200
        plan = plan_resp.json()
        sentences = plan["summary"]["sentences"]

        expected_sentence = (
            f"Your nearest achievement milestone is '{nearest['title']}' "
            f"({nearest['progress']['current']} of {nearest['progress']['target']} completed)."
        )

        assert expected_sentence in sentences, (
            f"For {email}, expected sentence:\n  {expected_sentence!r}\n"
            f"Actual sentences:\n  {sentences}"
        )
        assert nearest["title"] in allowed_titles

        real_db_client.post("/api/auth/logout")


def test_study_plan_ontime_habit_counts_only_ontime_submissions(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """On-time habit milestone counts only submissions on or before due date."""
    student, _ = create_test_student(real_db_session, "stu_ontime@test.com")
    inst = User(
        email="inst_ontime@test.com",
        full_name="Prof. Ontime",
        role=UserRole.INSTRUCTOR,
        password_hash=hash_password("testpass123"),
        is_active=True,
    )
    real_db_session.add(inst)
    real_db_session.flush()

    course = Course(
        instructor_id=inst.id,
        title="Ontime Course",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.flush()
    real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    real_db_session.flush()

    now = datetime.now(UTC)
    a1 = Assignment(
        course_id=course.id,
        title="Assignment 1",
        due_at=now + timedelta(days=2),
        max_points=50,
    )
    a2 = Assignment(
        course_id=course.id,
        title="Assignment 2",
        due_at=now + timedelta(days=3),
        max_points=50,
    )
    a3 = Assignment(
        course_id=course.id,
        title="Assignment 3",
        due_at=now - timedelta(days=1),
        max_points=50,
    )
    real_db_session.add_all([a1, a2, a3])
    real_db_session.flush()

    # 2 on-time submissions and 1 late submission
    sub1 = Submission(
        assignment_id=a1.id,
        student_id=student.id,
        content="code 1",
        is_late=False,
    )
    sub2 = Submission(
        assignment_id=a2.id,
        student_id=student.id,
        content="code 2",
        is_late=False,
    )
    sub3 = Submission(
        assignment_id=a3.id,
        student_id=student.id,
        content="code 3",
        is_late=True,
    )
    real_db_session.add_all([sub1, sub2, sub3])
    real_db_session.commit()

    login_test_user(real_db_client, "stu_ontime@test.com")

    badges_resp = real_db_client.get("/api/students/me/badges")
    assert badges_resp.status_code == 200
    badges_map = {b["id"]: b for b in badges_resp.json()}

    ontime_badge = badges_map["ontime_habit"]
    # Exactly 2 on-time submissions, NOT 3
    assert ontime_badge["progress"]["current"] == 2
    assert ontime_badge["progress"]["target"] == 5
    assert ontime_badge["title"] == "On-time habit"

    plan_resp = real_db_client.get("/api/students/me/study-plan?days=7")
    assert plan_resp.status_code == 200
    plan_sentences = plan_resp.json()["summary"]["sentences"]

    # Either Course finisher (3 of 3 -> earned) or On-time habit is nearest
    # All 3 assignments submitted in this course means course_finisher is earned
    assert badges_map["course_finisher"]["earned"] is True

    # Therefore On-time habit is the highest-ratio unearned countable badge (2 of 5 = 40%)
    expected_sentence = "Your nearest achievement milestone is 'On-time habit' (2 of 5 completed)."
    assert expected_sentence in plan_sentences


def test_study_plan_summary_when_all_badges_unlocked() -> None:
    """When a student has unlocked all badges, summary reflects full completion."""
    from app.schemas.badge import BadgeProgress, BadgeResponse
    from app.services.study_plan_summary import build_study_plan_summary

    all_badges = [
        BadgeResponse(
            id=d["id"],
            title=d["title"],
            description=d["description"],
            earned=True,
            progress=BadgeProgress(current=1, target=1) if d.get("target") else None,
        )
        for d in BADGE_DEFINITIONS
    ]

    summary = build_study_plan_summary(
        days=7,
        due_in_window=0,
        overdue_count=0,
        tight_count=0,
        course_grades=[],
        badges=all_badges,
        app_status_counts={},
        open_internships_count=0,
        enrolled_courses_count=1,
        total_suggested_minutes=0,
    )

    assert "You have unlocked all available achievement badges." in summary.sentences


def test_badge_titles_canonical_and_consistent() -> None:
    """Verify the 8 canonical badge titles are strictly consistent across service and schema."""
    expected_titles = [
        "First submission",
        "On-time habit",
        "High achiever",
        "Perfect score",
        "Course finisher",
        "Profile complete",
        "First application",
        "Offer accepted",
    ]
    actual_titles = [d["title"] for d in BADGE_DEFINITIONS]
    assert actual_titles == expected_titles

