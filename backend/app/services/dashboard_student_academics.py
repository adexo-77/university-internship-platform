"""Academics aggregation queries for student dashboard (due next, grades, progress)."""

from datetime import UTC, datetime

from sqlalchemy import Float, exists, func, select
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User
from app.schemas.dashboard_student import (
    StudentCourseProgressItem,
    StudentDueNextItem,
    StudentRecentGradeItem,
)


def get_student_due_next(db: Session, student_id: int) -> list[StudentDueNextItem]:
    """Fetch up to 5 upcoming unsubmitted assignments for enrolled published courses."""
    now = datetime.now(UTC)
    has_submitted = exists(
        select(1).where(
            Submission.assignment_id == Assignment.id,
            Submission.student_id == student_id,
        )
    )

    due_stmt = (
        select(
            Assignment.id.label("assignment_id"),
            Assignment.title.label("title"),
            Course.id.label("course_id"),
            Course.title.label("course_title"),
            Assignment.due_at.label("due_at"),
        )
        .join(Course, Assignment.course_id == Course.id)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(
            Enrollment.student_id == student_id,
            Course.status == CourseStatus.PUBLISHED,
            Assignment.due_at > now,
            ~has_submitted,
        )
        .order_by(Assignment.due_at.asc(), Assignment.id.asc())
        .limit(5)
    )
    return [
        StudentDueNextItem(
            assignment_id=row.assignment_id,
            title=row.title,
            course_id=row.course_id,
            course_title=row.course_title,
            due_at=row.due_at,
        )
        for row in db.execute(due_stmt).all()
    ]


def get_student_recent_grades(db: Session, student_id: int) -> list[StudentRecentGradeItem]:
    """Fetch up to 5 recently graded submissions for the student."""
    grades_stmt = (
        select(
            Submission.id.label("submission_id"),
            Assignment.id.label("assignment_id"),
            Assignment.title.label("assignment_title"),
            Course.title.label("course_title"),
            Submission.grade.label("grade"),
            Assignment.max_points.label("max_points"),
            Submission.graded_at.label("graded_at"),
        )
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .where(
            Submission.student_id == student_id,
            Submission.grade.is_not(None),
        )
        .order_by(
            func.coalesce(Submission.graded_at, Submission.updated_at).desc(),
            Submission.id.desc(),
        )
        .limit(5)
    )
    return [
        StudentRecentGradeItem(
            submission_id=row.submission_id,
            assignment_id=row.assignment_id,
            assignment_title=row.assignment_title,
            course_title=row.course_title,
            grade=row.grade,
            max_points=row.max_points,
            graded_at=row.graded_at,
        )
        for row in db.execute(grades_stmt).all()
    ]


def get_student_course_progress(db: Session, student_id: int) -> list[StudentCourseProgressItem]:
    """Fetch enrolled published courses with completion and grade metrics."""
    enrolled_courses = db.execute(
        select(Course.id, Course.title, User.full_name.label("instructor_name"))
        .join(Enrollment, Enrollment.course_id == Course.id)
        .outerjoin(User, Course.instructor_id == User.id)
        .where(
            Enrollment.student_id == student_id,
            Course.status == CourseStatus.PUBLISHED,
        )
        .order_by(Course.title.asc(), Course.id.asc())
    ).all()

    if not enrolled_courses:
        return []

    course_ids = [c.id for c in enrolled_courses]
    total_stmt = (
        select(Assignment.course_id, func.count(Assignment.id).label("total"))
        .where(Assignment.course_id.in_(course_ids))
        .group_by(Assignment.course_id)
    )
    totals_map = {row.course_id: row.total for row in db.execute(total_stmt).all()}

    sub_stmt = (
        select(
            Assignment.course_id,
            func.count(Submission.id).label("submitted_count"),
            func.count(Submission.grade).label("graded_count"),
            func.avg(
                (func.cast(Submission.grade, Float) / func.cast(Assignment.max_points, Float))
                * 100.0
            ).label("avg_grade_pct"),
        )
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .where(
            Submission.student_id == student_id,
            Assignment.course_id.in_(course_ids),
        )
        .group_by(Assignment.course_id)
    )
    subs_map = {row.course_id: row for row in db.execute(sub_stmt).all()}

    progress_list: list[StudentCourseProgressItem] = []
    for c in enrolled_courses:
        tot = totals_map.get(c.id, 0)
        sub_info = subs_map.get(c.id)
        submitted_count = sub_info.submitted_count if sub_info else 0
        prog = round((submitted_count / tot) * 100.0, 1) if tot > 0 else 0.0
        avg_grade = (
            round(float(sub_info.avg_grade_pct), 1)
            if sub_info and sub_info.graded_count > 0 and sub_info.avg_grade_pct is not None
            else None
        )
        progress_list.append(
            StudentCourseProgressItem(
                course_id=c.id,
                title=c.title,
                instructor_name=c.instructor_name,
                assignments_total=tot,
                assignments_submitted=submitted_count,
                progress_percent=prog,
                average_grade_percent=avg_grade,
            )
        )
    return progress_list
