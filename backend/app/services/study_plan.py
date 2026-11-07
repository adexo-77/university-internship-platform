"""Domain service for aggregating student commitments into a rule-based study plan."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User
from app.schemas.study_plan import StudyPlanDay, StudyPlanItem, StudyPlanResponse, StudyPlanWindow
from app.services.badge import get_student_badges
from app.services.internship_suggestion import get_candidate_postings, get_internship_suggestions
from app.services.study_plan_scheduler import (
    DAILY_CAP_MINUTES,
    EFFORT_HIGH_MINUTES,
    EFFORT_LOW_MAX_POINTS,
    EFFORT_LOW_MINUTES,
    EFFORT_MID_MAX_POINTS,
    EFFORT_MID_MINUTES,
    estimate_effort_minutes,
    schedule_pending_assignments,
)
from app.services.study_plan_summary import STUDY_PLAN_RULES, build_study_plan_summary

# Re-export named constants for API consumers and test suites
__all__ = [
    "DAILY_CAP_MINUTES",
    "DEFAULT_PLAN_DAYS",
    "EFFORT_HIGH_MINUTES",
    "EFFORT_LOW_MAX_POINTS",
    "EFFORT_LOW_MINUTES",
    "EFFORT_MID_MAX_POINTS",
    "EFFORT_MID_MINUTES",
    "MAX_PLAN_DAYS",
    "MIN_PLAN_DAYS",
    "STUDY_PLAN_RULES",
    "estimate_effort_minutes",
    "generate_study_plan",
]

# Window boundaries in days
DEFAULT_PLAN_DAYS: int = 7
MIN_PLAN_DAYS: int = 3
MAX_PLAN_DAYS: int = 14


def _is_profile_complete(profile: StudentProfile | None) -> bool:
    """Check whether mandatory university and department profile fields are non-empty."""
    return bool(
        profile
        and profile.university
        and profile.university.strip()
        and profile.department
        and profile.department.strip()
    )


def generate_study_plan(
    db: Session,
    student: User | int,
    days: int = DEFAULT_PLAN_DAYS,
    current_time: datetime | None = None,
) -> StudyPlanResponse:
    """Generate a deterministic, rule-based study schedule across the requested window."""
    if isinstance(student, User):
        student_id = student.id
        student_user = student
    else:
        student_id = student
        student_user = db.scalar(select(User).where(User.id == student_id))

    now = current_time or datetime.now(UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    today = now.date()
    window_end_date = today + timedelta(days=days - 1)
    window_dates = [today + timedelta(days=i) for i in range(days)]

    # 1. Enrolled published courses (Query 1)
    courses_stmt = (
        select(Course.id, Course.title)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.student_id == student_id, Course.status == CourseStatus.PUBLISHED)
        .order_by(Course.title.asc(), Course.id.asc())
    )
    enrolled_courses = db.execute(courses_stmt).all()
    course_ids = [c.id for c in enrolled_courses]
    course_title_map = {c.id: c.title for c in enrolled_courses}

    # 2. Assignments for enrolled courses (Query 2)
    assignments = (
        list(db.scalars(select(Assignment).where(Assignment.course_id.in_(course_ids))).all())
        if course_ids
        else []
    )

    # 3. Existing submissions by the student (Query 3)
    submissions = (
        list(
            db.scalars(
                select(Submission).where(
                    Submission.student_id == student_id,
                    Submission.assignment_id.in_([a.id for a in assignments]),
                )
            ).all()
        )
        if assignments
        else []
    )
    submitted_assignment_ids = {s.assignment_id for s in submissions}

    # Calculate average course grades for summary
    course_grades_data: list[dict[str, object]] = []
    for cid in course_ids:
        c_subs = [
            s
            for s in submissions
            if s.grade is not None
            and any(a.id == s.assignment_id and a.course_id == cid for a in assignments)
        ]
        if c_subs:
            avg_val = sum(s.grade for s in c_subs) / len(c_subs)
            course_grades_data.append(
                {"title": course_title_map.get(cid, "Course"), "avg": avg_val}
            )

    # Pending assignments are those without a submission (graded and submitted excluded)
    pending_assignments = [a for a in assignments if a.id not in submitted_assignment_ids]

    # Run deterministic scheduling algorithm
    day_items, overdue_list, tight_list = schedule_pending_assignments(
        pending_assignments=pending_assignments,
        course_title_map=course_title_map,
        window_dates=window_dates,
        now=now,
    )

    # 4. Profile check (Query 4)
    prof = db.scalar(select(StudentProfile).where(StudentProfile.user_id == student_id))
    profile_complete = _is_profile_complete(prof)

    # 5. Student applications (Query 5)
    apps = db.execute(
        select(Application.status, Application.posting_id).where(
            Application.student_id == student_id
        )
    ).all()
    applied_ids = {row.posting_id for row in apps}
    app_status_counts = Counter(
        row.status.value if hasattr(row.status, "value") else str(row.status) for row in apps
    )

    # 6. Suggested internships (bounded suggestions)
    suggestions_items = (
        get_internship_suggestions(db, student_user, limit=20).items if student_user else []
    )
    cands: list[tuple[int, str, str | None, datetime | None]] = [
        (s.id, s.title, s.organization_name, s.application_deadline) for s in suggestions_items
    ]
    if not cands and student_user and not profile_complete:
        raw_cands = get_candidate_postings(db, student_user.id)
        cands = [(p.id, p.title, org, p.application_deadline) for p, org in raw_cands[:20]]

    internship_items_count = 0
    for int_id, title, org_name, dl in cands:
        if int_id in applied_ids or not dl:
            continue
        dl_utc = dl if dl.tzinfo is not None else dl.replace(tzinfo=UTC)
        dl_date = dl_utc.date()
        if today <= dl_date <= window_end_date:
            internship_items_count += 1
            reason_text = f"Apply by {dl_utc.strftime('%d %b %Y')}"
            int_flags: list[str] = []
            if not profile_complete:
                reason_text += " (Complete your profile to apply)"
                int_flags.append("profile_incomplete")
            day_items[dl_date].append(
                StudyPlanItem(
                    id=f"internship-{int_id}",
                    type="internship",
                    title=f"Apply: {title}",
                    course_title=org_name,
                    link_path=f"/internships/{int_id}",
                    due_at=dl_utc,
                    suggested_minutes=0,
                    reason=reason_text,
                    flags=int_flags,
                )
            )

    # 7. Student achievement badges (bounded calculation)
    badges = get_student_badges(db, student_user) if student_user else []

    # Assemble plan days
    plan: list[StudyPlanDay] = []
    total_minutes = 0
    for d in window_dates:
        items = day_items[d]
        d_min = sum(i.suggested_minutes for i in items)
        total_minutes += d_min
        plan.append(StudyPlanDay(date=d, items=items, total_minutes=d_min))

    due_in_window = sum(
        1
        for a in pending_assignments
        if today <= a.due_at.date() <= window_end_date and a.due_at >= now
    )

    summary = build_study_plan_summary(
        days=days,
        due_in_window=due_in_window,
        overdue_count=len(overdue_list),
        tight_count=len(tight_list),
        course_grades=course_grades_data,
        badges=badges,
        app_status_counts=app_status_counts,
        open_internships_count=internship_items_count,
        enrolled_courses_count=len(enrolled_courses),
        total_suggested_minutes=total_minutes,
    )

    return StudyPlanResponse(
        generated_at=now,
        window=StudyPlanWindow(start_date=today, end_date=window_end_date, days=days),
        summary=summary,
        plan=plan,
        overdue=overdue_list,
        tight=tight_list,
        rules=STUDY_PLAN_RULES,
    )
