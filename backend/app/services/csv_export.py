"""Domain queries and CSV generation for gradebooks, applicants, and reports."""

from fastapi import Response
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import select

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.internship import Internship
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.services.csv_export_writer import MAX_CSV_ROWS, build_csv_response


def export_course_gradebook_csv(db: Session, course_id: int, current_user: User) -> Response:
    """Export gradebook CSV for owner instructor or admin."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    is_owner = current_user.role == UserRole.INSTRUCTOR and course.instructor_id == current_user.id
    if current_user.role != UserRole.ADMIN and not is_owner:
        raise ForbiddenException(
            message="Only the course instructor or an administrator can export the gradebook",
            code="FORBIDDEN",
        )

    assignments = list(
        db.scalars(
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.due_at.asc(), Assignment.id.asc())
        )
    )
    enrollments = list(
        db.execute(
            select(Enrollment, User)
            .join(User, Enrollment.student_id == User.id)
            .where(Enrollment.course_id == course_id)
            .order_by(User.full_name.asc(), User.id.asc())
            .limit(MAX_CSV_ROWS)
        ).all()
    )

    assignment_ids = [a.id for a in assignments]
    sub_map: dict[tuple[int, int], Submission] = {}
    if assignment_ids:
        subs = list(
            db.scalars(select(Submission).where(Submission.assignment_id.in_(assignment_ids)))
        )
        for s in subs:
            sub_map[(s.student_id, s.assignment_id)] = s

    headers = (
        ["Student Name", "Email"]
        + [a.title for a in assignments]
        + ["Submitted Count", "Graded Count", "Average Percent"]
    )
    rows: list[list[object]] = []
    for _, student in enrollments:
        submitted_count, graded_count, pct_sum = 0, 0, 0.0
        row: list[object] = [student.full_name, student.email]
        for a in assignments:
            sub = sub_map.get((student.id, a.id))
            if sub and sub.grade is not None:
                submitted_count += 1
                graded_count += 1
                pct_sum += (sub.grade / a.max_points) * 100 if a.max_points > 0 else 0.0
                row.append(sub.grade)
            elif sub:
                submitted_count += 1
                row.append("")
            else:
                row.append("")

        avg_str = f"{round(pct_sum / graded_count, 1)}%" if graded_count > 0 else ""
        row.extend([submitted_count, graded_count, avg_str])
        rows.append(row)

    return build_csv_response(headers, rows, f"course_{course_id}_gradebook.csv")


def export_internship_applicants_csv(
    db: Session, internship_id: int, current_user: User
) -> Response:
    """Export applicant roster CSV for owner organization, admin, or coordinator."""
    posting = db.scalar(select(Internship).where(Internship.id == internship_id))
    if not posting:
        raise NotFoundException(message="Internship posting not found", code="INTERNSHIP_NOT_FOUND")

    is_owner = (
        current_user.role == UserRole.ORGANIZATION and posting.organization_id == current_user.id
    )
    is_staff = current_user.role in (UserRole.ADMIN, UserRole.COORDINATOR)
    if not is_owner and not is_staff:
        raise ForbiddenException(
            message="Not authorized to export applicants for this posting",
            code="FORBIDDEN",
        )

    records = list(
        db.execute(
            select(Application, User, StudentProfile)
            .join(User, Application.student_id == User.id)
            .outerjoin(StudentProfile, User.id == StudentProfile.user_id)
            .where(Application.posting_id == internship_id)
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(MAX_CSV_ROWS)
        ).all()
    )

    headers = [
        "Applicant Name",
        "Email",
        "University",
        "Department",
        "Year of Study",
        "Status",
        "Applied Date",
    ]
    rows: list[list[object]] = [
        [
            student.full_name,
            student.email,
            profile.university if profile and profile.university else "",
            profile.department if profile and profile.department else "",
            profile.year_of_study if profile and profile.year_of_study else "",
            app.status.value,
            app.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        for app, student, profile in records
    ]
    return build_csv_response(headers, rows, f"internship_{internship_id}_applicants.csv")


def export_applications_report_csv(db: Session, current_user: User) -> Response:
    """Export platform applications report CSV for admin or coordinator."""
    if current_user.role not in (UserRole.ADMIN, UserRole.COORDINATOR):
        raise ForbiddenException(
            message="Only administrators or coordinators can access applications reports",
            code="FORBIDDEN",
        )

    org_user = aliased(User, name="org_user")
    student_user = aliased(User, name="student_user")
    records = list(
        db.execute(
            select(Application, Internship, org_user, student_user)
            .join(Internship, Application.posting_id == Internship.id)
            .join(org_user, Internship.organization_id == org_user.id)
            .join(student_user, Application.student_id == student_user.id)
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(MAX_CSV_ROWS)
        ).all()
    )

    headers = ["Posting", "Organization", "Applicant", "Status", "Applied Date", "Decided Date"]
    rows: list[list[object]] = [
        [
            posting.title,
            org.full_name,
            applicant.full_name,
            app.status.value,
            app.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            app.decided_at.strftime("%Y-%m-%d %H:%M:%S") if app.decided_at else "",
        ]
        for app, posting, org, applicant in records
    ]
    return build_csv_response(headers, rows, "applications_report.csv")


def export_users_report_csv(db: Session, current_user: User) -> Response:
    """Export users list CSV for admin only (never password hashes or tokens)."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(
            message="Only administrators can export user reports",
            code="FORBIDDEN",
        )

    users = list(db.scalars(select(User).order_by(User.id.asc()).limit(MAX_CSV_ROWS)))
    headers = ["ID", "Name", "Email", "Role", "Active", "Created Date"]
    rows = [
        [
            u.id,
            u.full_name,
            u.email,
            u.role.value,
            str(u.is_active).lower(),
            u.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        for u in users
    ]
    return build_csv_response(headers, rows, "users_report.csv")
