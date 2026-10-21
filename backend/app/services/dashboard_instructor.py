"""Domain service for aggregating instructor dashboard metrics."""

from sqlalchemy import Float, case, func, select
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User
from app.schemas.dashboard_instructor import (
    InstructorCourseItem,
    InstructorDashboardResponse,
    InstructorNeedsGradingItem,
)


def get_instructor_dashboard(db: Session, instructor_id: int) -> InstructorDashboardResponse:
    """Aggregate dashboard metrics for an instructor."""
    courses = db.execute(
        select(Course.id, Course.title, Course.status)
        .where(Course.instructor_id == instructor_id)
        .order_by(Course.created_at.desc(), Course.id.desc())
    ).all()

    course_items: list[InstructorCourseItem] = []
    if courses:
        course_ids = [c.id for c in courses]

        # Enrolled student count per course
        enrollment_stmt = (
            select(Enrollment.course_id, func.count(Enrollment.id).label("count"))
            .where(Enrollment.course_id.in_(course_ids))
            .group_by(Enrollment.course_id)
        )
        enrolled_map = {r.course_id: r.count for r in db.execute(enrollment_stmt).all()}

        # Total assignments count per course
        assignment_stmt = (
            select(Assignment.course_id, func.count(Assignment.id).label("count"))
            .where(Assignment.course_id.in_(course_ids))
            .group_by(Assignment.course_id)
        )
        assignments_map = {r.course_id: r.count for r in db.execute(assignment_stmt).all()}

        # Awaiting grading & graded metrics per course
        sub_metrics_stmt = (
            select(
                Assignment.course_id,
                func.sum(case((Submission.grade.is_(None), 1), else_=0)).label("awaiting"),
                func.sum(case((Submission.grade.is_not(None), 1), else_=0)).label("graded"),
                func.avg(
                    case(
                        (
                            Submission.grade.is_not(None),
                            (
                                func.cast(Submission.grade, Float)
                                / func.cast(Assignment.max_points, Float)
                            )
                            * 100.0,
                        ),
                        else_=None,
                    )
                ).label("avg_pct"),
            )
            .join(Assignment, Submission.assignment_id == Assignment.id)
            .where(Assignment.course_id.in_(course_ids))
            .group_by(Assignment.course_id)
        )
        sub_metrics_map = {r.course_id: r for r in db.execute(sub_metrics_stmt).all()}

        for c in courses:
            sub_m = sub_metrics_map.get(c.id)
            awaiting = int(sub_m.awaiting) if sub_m and sub_m.awaiting else 0
            graded_count = int(sub_m.graded) if sub_m and sub_m.graded else 0
            avg_grade = (
                round(float(sub_m.avg_pct), 1)
                if sub_m and graded_count > 0 and sub_m.avg_pct is not None
                else None
            )

            course_items.append(
                InstructorCourseItem(
                    course_id=c.id,
                    title=c.title,
                    status=c.status.value if hasattr(c.status, "value") else str(c.status),
                    enrolled_count=enrolled_map.get(c.id, 0),
                    assignments_count=assignments_map.get(c.id, 0),
                    submissions_awaiting_grading=awaiting,
                    average_grade_percent=avg_grade,
                )
            )

    # 2. needs_grading: up to 10 oldest ungraded submitted submissions
    needs_grading_stmt = (
        select(
            Submission.id.label("submission_id"),
            User.full_name.label("student_name"),
            Assignment.id.label("assignment_id"),
            Assignment.title.label("assignment_title"),
            Course.id.label("course_id"),
            Course.title.label("course_title"),
            Submission.submitted_at.label("submitted_at"),
            Submission.is_late.label("late"),
        )
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .join(User, Submission.student_id == User.id)
        .where(
            Course.instructor_id == instructor_id,
            Submission.grade.is_(None),
        )
        .order_by(Submission.submitted_at.asc(), Submission.id.asc())
        .limit(10)
    )
    needs_grading_rows = db.execute(needs_grading_stmt).all()
    needs_grading = [
        InstructorNeedsGradingItem(
            submission_id=r.submission_id,
            student_name=r.student_name,
            assignment_id=r.assignment_id,
            assignment_title=r.assignment_title,
            course_id=r.course_id,
            course_title=r.course_title,
            submitted_at=r.submitted_at,
            late=r.late,
        )
        for r in needs_grading_rows
    ]

    return InstructorDashboardResponse(
        courses=course_items,
        needs_grading=needs_grading,
    )
