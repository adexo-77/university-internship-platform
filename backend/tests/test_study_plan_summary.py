"""Unit and rule tests for study plan summary sentence generation."""

from collections import Counter

from app.services.study_plan_summary import build_study_plan_summary


def test_application_wording_multi_status_breakdown() -> None:
    """Multi-status applications do not use 'active' and format breakdown correctly."""
    app_counts = Counter({"submitted": 1, "rejected": 1, "withdrawn": 1})
    summary = build_study_plan_summary(
        days=7,
        due_in_window=0,
        overdue_count=0,
        tight_count=0,
        course_grades=[],
        badges=[],
        app_status_counts=app_counts,
        open_internships_count=0,
        enrolled_courses_count=1,
        total_suggested_minutes=0,
    )
    expected = "You have 3 applications: 1 rejected, 1 submitted, 1 withdrawn."
    assert expected in summary.sentences
    assert not any("active" in s.lower() for s in summary.sentences)


def test_application_wording_single_application() -> None:
    """Single application formats singular noun without 'active'."""
    app_counts = Counter({"submitted": 1})
    summary = build_study_plan_summary(
        days=7,
        due_in_window=0,
        overdue_count=0,
        tight_count=0,
        course_grades=[],
        badges=[],
        app_status_counts=app_counts,
        open_internships_count=0,
        enrolled_courses_count=1,
        total_suggested_minutes=0,
    )
    assert "You have 1 application: 1 submitted." in summary.sentences
    assert not any("active" in s.lower() for s in summary.sentences)


def test_application_wording_zero_applications_shows_open_or_none() -> None:
    """Zero applications mentions open opportunities if available or none submitted."""
    summary_open = build_study_plan_summary(
        days=7,
        due_in_window=0,
        overdue_count=0,
        tight_count=0,
        course_grades=[],
        badges=[],
        app_status_counts=Counter(),
        open_internships_count=2,
        enrolled_courses_count=1,
        total_suggested_minutes=0,
    )
    assert any("open internship application deadlines" in s for s in summary_open.sentences)

    summary_none = build_study_plan_summary(
        days=7,
        due_in_window=0,
        overdue_count=0,
        tight_count=0,
        course_grades=[],
        badges=[],
        app_status_counts=Counter(),
        open_internships_count=0,
        enrolled_courses_count=1,
        total_suggested_minutes=0,
    )
    assert "You have not submitted any internship applications yet." in summary_none.sentences
