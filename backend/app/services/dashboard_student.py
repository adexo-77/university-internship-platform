"""Domain service for aggregating student dashboard metrics."""

from datetime import UTC, datetime

from sqlalchemy import Float, exists, func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.internship import Internship
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User
from app.schemas.dashboard_student import (
    StudentApplicationRecentItem,
    StudentApplicationsSummary,
    StudentCourseProgressItem,
    StudentDashboardResponse,
    StudentDueNextItem,
    StudentRecentGradeItem,
)


def get_student_dashboard(db: Session, student_id: int) -> StudentDashboardResponse:
    """Aggregate dashboard metrics for an authenticated student."""
    now = datetime.now(UTC)

    # 1. due_next: up to 5 assignments from enrolled published courses not yet submitted
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
    due_rows = db.execute(due_stmt).all()
    due_next = [
        StudentDueNextItem(
            assignment_id=row.assignment_id,
            title=row.title,
            course_id=row.course_id,
            course_title=row.course_title,
            due_at=row.due_at,
        )
        for row in due_rows
    ]

    # 2. recent_grades: up to 5 latest graded submissions
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
    grade_rows = db.execute(grades_stmt).all()
    recent_grades = [
        StudentRecentGradeItem(
            submission_id=row.submission_id,
            assignment_id=row.assignment_id,
            assignment_title=row.assignment_title,
            course_title=row.course_title,
            grade=row.grade,
            max_points=row.max_points,
            graded_at=row.graded_at,
        )
        for row in grade_rows
    ]

    # 3. courses: enrolled published courses progress & grade average
    enrolled_courses = db.execute(
        select(Course.id, Course.title)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(
            Enrollment.student_id == student_id,
            Course.status == CourseStatus.PUBLISHED,
        )
        .order_by(Course.title.asc(), Course.id.asc())
    ).all()

    course_progress_list: list[StudentCourseProgressItem] = []
    if enrolled_courses:
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
            course_progress_list.append(
                StudentCourseProgressItem(
                    course_id=c.id,
                    title=c.title,
                    assignments_total=tot,
                    assignments_submitted=submitted_count,
                    progress_percent=prog,
                    average_grade_percent=avg_grade,
                )
            )

    # 4. applications: status counts and 3 latest
    app_counts_stmt = (
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.student_id == student_id)
        .group_by(Application.status)
    )
    app_counts_map = {status.value: 0 for status in ApplicationStatus}
    for row in db.execute(app_counts_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        app_counts_map[key] = row.count

    recent_apps_stmt = (
        select(
            Application.id,
            Application.posting_id,
            Internship.title.label("posting_title"),
            func.coalesce(
                OrganizationProfile.organization_name,
                User.full_name,
            ).label("organization_name"),
            Application.status,
            Application.created_at.label("applied_at"),
        )
        .join(Internship, Application.posting_id == Internship.id)
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, OrganizationProfile.user_id == User.id)
        .where(Application.student_id == student_id)
        .order_by(Application.created_at.desc(), Application.id.desc())
        .limit(3)
    )
    recent_app_rows = db.execute(recent_apps_stmt).all()
    recent_apps = [
        StudentApplicationRecentItem(
            id=row.id,
            posting_id=row.posting_id,
            posting_title=row.posting_title,
            organization_name=row.organization_name,
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            applied_at=row.applied_at,
        )
        for row in recent_app_rows
    ]

    # 5. profile_complete: true when university and department are filled
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == student_id))
    profile_complete = bool(
        profile
        and profile.university
        and profile.university.strip()
        and profile.department
        and profile.department.strip()
    )

    return StudentDashboardResponse(
        due_next=due_next,
        recent_grades=recent_grades,
        courses=course_progress_list,
        applications=StudentApplicationsSummary(
            counts_by_status=app_counts_map,
            recent=recent_apps,
        ),
        profile_complete=profile_complete,
    )
