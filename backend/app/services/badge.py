"""Business logic for computing student achievement badges on read."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.assignment import Assignment
from app.models.enrollment import Enrollment
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User
from app.schemas.badge import BadgeProgress, BadgeResponse

BADGE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "first_submission",
        "title": "First submission",
        "description": "Submitted at least one assignment coursework.",
        "countable": True,
        "target": 1,
    },
    {
        "id": "ontime_habit",
        "title": "On-time habit",
        "description": "Submitted 5 assignments on or before the due date.",
        "countable": True,
        "target": 5,
    },
    {
        "id": "high_achiever",
        "title": "High achiever",
        "description": "Achieved a grade of 90% or higher on an assignment.",
        "countable": False,
        "target": None,
    },
    {
        "id": "perfect_score",
        "title": "Perfect score",
        "description": "Achieved a grade equal to the maximum possible points.",
        "countable": False,
        "target": None,
    },
    {
        "id": "course_finisher",
        "title": "Course finisher",
        "description": "Submitted all assignments of a course with at least one assignment.",
        "countable": True,
        "target": None,
    },
    {
        "id": "profile_complete",
        "title": "Profile complete",
        "description": "Completed university, department, year of study, bio, and skills.",
        "countable": True,
        "target": 5,
    },
    {
        "id": "first_application",
        "title": "First application",
        "description": "Submitted at least one internship application.",
        "countable": True,
        "target": 1,
    },
    {
        "id": "offer_accepted",
        "title": "Offer accepted",
        "description": "Accepted an offer for an internship position.",
        "countable": True,
        "target": 1,
    },
]


def _compute_course_finisher(db: Session, student_id: int) -> tuple[bool, BadgeProgress | None]:
    """Check if all assignments of any course with >=1 assignment were submitted."""
    enrolled_course_ids = list(
        db.scalars(select(Enrollment.course_id).where(Enrollment.student_id == student_id))
    )
    if not enrolled_course_ids:
        return False, None

    best_ratio = -1.0
    best_current = 0
    best_target = 0

    for cid in enrolled_course_ids:
        assignment_ids = list(db.scalars(select(Assignment.id).where(Assignment.course_id == cid)))
        total = len(assignment_ids)
        if total == 0:
            continue

        submitted = (
            db.scalar(
                select(func.count(Submission.id)).where(
                    Submission.student_id == student_id,
                    Submission.assignment_id.in_(assignment_ids),
                )
            )
            or 0
        )

        ratio = submitted / total
        if submitted >= total:
            return True, BadgeProgress(current=total, target=total)

        if ratio > best_ratio:
            best_ratio = ratio
            best_current = submitted
            best_target = total

    if best_target > 0:
        return False, BadgeProgress(current=best_current, target=best_target)
    return False, None


def _compute_profile_complete(db: Session, student_id: int) -> tuple[bool, BadgeProgress]:
    """Check completion of university, department, year, bio, and skills."""
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == student_id))
    checks = [
        bool(profile and profile.university and profile.university.strip()),
        bool(profile and profile.department and profile.department.strip()),
        bool(profile and profile.year_of_study is not None),
        bool(profile and profile.bio and profile.bio.strip()),
        bool(profile and profile.skills and len(profile.skills) > 0),
    ]
    filled = sum(checks)
    return filled == 5, BadgeProgress(current=filled, target=5)


def get_student_badges(db: Session, student: User) -> list[BadgeResponse]:
    """Compute and return all achievement badges for the authenticated student."""
    sid = student.id

    # Submissions query
    sub_stats = db.execute(
        select(
            func.count(Submission.id),
            func.count(Submission.id).filter(Submission.is_late.is_(False)),
        ).where(Submission.student_id == sid)
    ).one()
    total_subs = sub_stats[0] or 0
    ontime_subs = sub_stats[1] or 0

    # High achiever & perfect score checks
    graded_subs = list(
        db.execute(
            select(Submission.grade, Assignment.max_points)
            .join(Assignment, Submission.assignment_id == Assignment.id)
            .where(Submission.student_id == sid, Submission.grade.is_not(None))
        ).all()
    )
    has_high_achiever = any(mp > 0 and (grade / mp) >= 0.90 for grade, mp in graded_subs)
    has_perfect_score = any(mp > 0 and grade == mp for grade, mp in graded_subs)

    # Applications query
    app_stats = db.execute(
        select(
            func.count(Application.id),
            func.count(Application.id).filter(Application.status == ApplicationStatus.ACCEPTED),
        ).where(Application.student_id == sid)
    ).one()
    total_apps = app_stats[0] or 0
    accepted_apps = app_stats[1] or 0

    course_finisher_earned, course_finisher_progress = _compute_course_finisher(db, sid)
    profile_complete_earned, profile_complete_progress = _compute_profile_complete(db, sid)

    results: list[BadgeResponse] = []
    for defn in BADGE_DEFINITIONS:
        bid = defn["id"]
        earned = False
        progress: BadgeProgress | None = None

        if bid == "first_submission":
            earned = total_subs >= 1
            progress = BadgeProgress(current=min(total_subs, 1), target=1)
        elif bid == "ontime_habit":
            earned = ontime_subs >= 5
            progress = BadgeProgress(current=min(ontime_subs, 5), target=5)
        elif bid == "high_achiever":
            earned = has_high_achiever
        elif bid == "perfect_score":
            earned = has_perfect_score
        elif bid == "course_finisher":
            earned = course_finisher_earned
            progress = course_finisher_progress
        elif bid == "profile_complete":
            earned = profile_complete_earned
            progress = profile_complete_progress
        elif bid == "first_application":
            earned = total_apps >= 1
            progress = BadgeProgress(current=min(total_apps, 1), target=1)
        elif bid == "offer_accepted":
            earned = accepted_apps >= 1
            progress = BadgeProgress(current=min(accepted_apps, 1), target=1)

        results.append(
            BadgeResponse(
                id=bid,
                title=defn["title"],
                description=defn["description"],
                earned=earned,
                progress=progress,
            )
        )

    return results
