"""Summary generation service for deterministic, rule-based student study plans."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.badge import BadgeResponse
    from app.schemas.study_plan import StudyPlanSummary

# Maximum and minimum sentence bounds for summary synthesis
MIN_SUMMARY_SENTENCES: int = 3
MAX_SUMMARY_SENTENCES: int = 5

STUDY_PLAN_RULES: list[str] = [
    "Pending assignments without submissions are prioritized by due date, point value, and ID.",
    (
        "Overdue coursework (passed deadline without submission) is flagged "
        "and scheduled starting today."
    ),
    (
        "Effort is estimated from assignment max points: up to 20 pts = 45 min, "
        "up to 50 pts = 90 min, above 50 pts = 150 min."
    ),
    (
        "Daily study effort is capped at 120 minutes per day, spread backwards "
        "from before the due date."
    ),
    "Work that cannot fit before its deadline is scheduled starting today and flagged as 'tight'.",
    "No preparation is scheduled after an assignment's due date.",
    (
        "Open suggested internships with deadlines in the window are included "
        "with application reminders."
    ),
    "Students with incomplete profiles receive guidance to complete their profile before applying.",
    (
        "This study plan is purely rule-based and deterministic; "
        "it uses no artificial intelligence or machine learning."
    ),
]


def compute_nearest_badge(badges: list[BadgeResponse]) -> BadgeResponse | None:
    """Find unearned countable badge with highest progress ratio towards its target."""
    best_badge: BadgeResponse | None = None
    best_ratio = -1.0
    for badge in badges:
        if badge.earned or not badge.progress or not badge.progress.target:
            continue
        target = badge.progress.target
        current = badge.progress.current or 0
        ratio = current / target if target > 0 else 0.0
        if ratio > best_ratio:
            best_ratio = ratio
            best_badge = badge
    return best_badge


def build_summary_sentences(
    days: int,
    due_in_window: int,
    overdue_count: int,
    tight_count: int,
    course_grades: list[dict[str, object]],
    nearest_badge: BadgeResponse | None,
    all_badges_earned: bool,
    app_status_counts: dict[str, int],
    open_internships_count: int,
    enrolled_courses_count: int,
) -> list[str]:
    """Assemble between 3 and 5 plain English sentences summarizing student status."""
    sentences: list[str] = []

    # 1. Coursework commitments sentence
    if overdue_count > 0:
        plural_ov = "assignments" if overdue_count != 1 else "assignment"
        sentences.append(
            f"You have {overdue_count} overdue {plural_ov} and {due_in_window} upcoming "
            f"coursework deadline{'s' if due_in_window != 1 else ''} scheduled in this "
            f"{days}-day window."
        )
    elif due_in_window > 0:
        plural = "assignments" if due_in_window != 1 else "assignment"
        sentences.append(
            f"You have {due_in_window} {plural} due across your enrolled courses "
            f"within the next {days} days."
        )
    else:
        sentences.append(
            f"There are no pending assignment deadlines scheduled in this {days}-day study window."
        )

    # 2. Academic progress and grades sentence
    if course_grades:
        avg_strings = [
            f"{c['title']}: {float(c['avg']):.1f}%"
            for c in course_grades
            if "title" in c and "avg" in c
        ]
        if avg_strings:
            sentences.append(f"Current course performance averages: {', '.join(avg_strings)}.")
        else:
            sentences.append("No numeric coursework grades have been recorded yet.")
    elif enrolled_courses_count > 0:
        sentences.append("No coursework grades have been recorded yet for your enrolled courses.")
    else:
        sentences.append("You are not currently enrolled in any published courses.")

    # 3. Nearest achievement badge sentence
    if nearest_badge and nearest_badge.progress and nearest_badge.progress.target:
        cur = nearest_badge.progress.current or 0
        tgt = nearest_badge.progress.target
        sentences.append(
            f"Your nearest achievement milestone is '{nearest_badge.title}' "
            f"({cur} of {tgt} completed)."
        )
    elif all_badges_earned:
        sentences.append("You have unlocked all available achievement badges.")
    else:
        sentences.append(
            "Submit coursework and apply for internships to unlock achievement badges."
        )

    # 4. Internship applications sentence
    total_apps = sum(app_status_counts.values())
    if total_apps > 0:
        breakdown_parts = [
            f"{cnt} {st}" for st, cnt in sorted(app_status_counts.items()) if cnt > 0
        ]
        sentences.append(
            f"You have {total_apps} application{'s' if total_apps != 1 else ''}: "
            f"{', '.join(breakdown_parts)}."
        )
    elif open_internships_count > 0:
        plural_int = "deadlines" if open_internships_count != 1 else "deadline"
        sentences.append(
            f"There are {open_internships_count} open internship application {plural_int} "
            f"matching your profile within this window."
        )
    else:
        sentences.append("You have not submitted any internship applications yet.")

    # 5. Conclusion sentence (if nothing to do or tight focus)
    if due_in_window == 0 and overdue_count == 0 and open_internships_count == 0:
        sentences.append(
            "There is nothing pending to do right now; review past course resources "
            "or explore new internships."
        )
    elif overdue_count > 0 or tight_count > 0:
        critical_count = overdue_count + tight_count
        sentences.append(
            f"Focus on the {critical_count} critical task{'s' if critical_count != 1 else ''} "
            "highlighted in your plan to keep your study schedule on track."
        )

    # Ensure output strictly stays within 3 to 5 sentences
    return sentences[:MAX_SUMMARY_SENTENCES]


def build_study_plan_summary(
    days: int,
    due_in_window: int,
    overdue_count: int,
    tight_count: int,
    course_grades: list[dict[str, object]],
    badges: list[BadgeResponse],
    app_status_counts: dict[str, int],
    open_internships_count: int,
    enrolled_courses_count: int,
    total_suggested_minutes: int,
) -> StudyPlanSummary:
    """Construct headline, plain sentences, and metrics for the study plan."""
    from app.schemas.study_plan import StudyPlanMetrics, StudyPlanSummary

    # Headline construction
    if overdue_count > 0:
        headline = (
            f"You have {overdue_count} overdue assignment{'s' if overdue_count != 1 else ''} "
            "needing immediate attention."
        )
    elif due_in_window > 0:
        headline = (
            f"{due_in_window} assignment{'s' if due_in_window != 1 else ''} scheduled "
            f"over the next {days} days."
        )
    elif open_internships_count > 0:
        plural_int = "deadlines" if open_internships_count != 1 else "deadline"
        headline = (
            f"{open_internships_count} internship {plural_int} approaching in the next {days} days."
        )
    else:
        headline = f"Your study schedule is clear for the next {days} days."

    nearest_badge = compute_nearest_badge(badges)
    all_earned = bool(badges) and all(b.earned for b in badges)

    sentences = build_summary_sentences(
        days=days,
        due_in_window=due_in_window,
        overdue_count=overdue_count,
        tight_count=tight_count,
        course_grades=course_grades,
        nearest_badge=nearest_badge,
        all_badges_earned=all_earned,
        app_status_counts=app_status_counts,
        open_internships_count=open_internships_count,
        enrolled_courses_count=enrolled_courses_count,
    )

    metrics = StudyPlanMetrics(
        enrolled_courses_count=enrolled_courses_count,
        assignments_due_count=due_in_window,
        overdue_count=overdue_count,
        tight_count=tight_count,
        total_suggested_minutes=total_suggested_minutes,
        applications_count=sum(app_status_counts.values()),
        open_internships_count=open_internships_count,
    )

    return StudyPlanSummary(
        headline=headline,
        sentences=sentences,
        metrics=metrics,
    )
