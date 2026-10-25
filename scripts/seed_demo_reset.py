"""Safe removal of demo accounts in foreign-key dependency order."""

from collections.abc import Iterable

from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.internship import Internship
from app.models.notification import Notification
from app.models.organization_profile import OrganizationProfile
from app.models.session import Session as UserSession
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

OLD_DEMO_EMAILS = [
    "demo.admin@example.com",
    "demo.instructor@example.com",
    "demo.student@example.com",
    "demo.student2@example.com",
    "demo.org@example.com",
    "demo.neworg@example.com",
]

NEW_DEMO_EMAILS = [
    "mulugeta.assefa@example.com",
    "selamawit.tadesse@example.com",
    "tadesse.bekele@example.com",
    "hana.worku@example.com",
    "abel.tesfaye@example.com",
    "meron.girma@example.com",
    "dawit.lemma@example.com",
    "yohannes.haile@example.com",
    "rahel.desta@example.com",
    "eyob.kassa@example.com",
]

ALL_DEMO_EMAILS: tuple[str, ...] = tuple(OLD_DEMO_EMAILS + NEW_DEMO_EMAILS)


def _collect_demo_scope(
    db: Session, user_ids: list[int]
) -> tuple[list[int], list[int], list[int]]:
    course_ids = db.scalars(
        select(Course.id).where(Course.instructor_id.in_(user_ids))
    ).all()
    assign_ids = db.scalars(
        select(Assignment.id).where(Assignment.course_id.in_(course_ids))
    ).all()
    posting_ids = db.scalars(
        select(Internship.id).where(Internship.organization_id.in_(user_ids))
    ).all()
    return list(course_ids), list(assign_ids), list(posting_ids)


def _delete_in_dependency_order(
    db: Session,
    user_ids: list[int],
    c_ids: Iterable[int],
    a_ids: Iterable[int],
    p_ids: Iterable[int],
) -> None:
    c_list, a_list, p_list = list(c_ids), list(a_ids), list(p_ids)

    # 1. Submissions by demo students or under demo assignments
    db.execute(
        delete(Submission).where(
            Submission.student_id.in_(user_ids) | Submission.assignment_id.in_(a_list)
        )
    )
    # 2. Applications by demo students or under demo postings
    db.execute(
        delete(Application).where(
            Application.student_id.in_(user_ids) | Application.posting_id.in_(p_list)
        )
    )
    # 3. Assignments and resources under demo courses
    db.execute(delete(Assignment).where(Assignment.course_id.in_(c_list)))
    db.execute(delete(CourseResource).where(CourseResource.course_id.in_(c_list)))
    # 4. Enrollments of demo students or in demo courses
    db.execute(
        delete(Enrollment).where(
            Enrollment.student_id.in_(user_ids) | Enrollment.course_id.in_(c_list)
        )
    )
    # 5. Internships by demo orgs
    db.execute(delete(Internship).where(Internship.organization_id.in_(user_ids)))
    # 6. Courses by demo instructors
    db.execute(delete(Course).where(Course.instructor_id.in_(user_ids)))
    # 7. Student and Org profiles for demo users
    db.execute(delete(StudentProfile).where(StudentProfile.user_id.in_(user_ids)))
    db.execute(
        delete(OrganizationProfile).where(OrganizationProfile.user_id.in_(user_ids))
    )
    # 8. Active sessions and notifications for demo users
    db.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
    db.execute(delete(Notification).where(Notification.user_id.in_(user_ids)))
    # 9. Demo users
    db.execute(delete(User).where(User.id.in_(user_ids)))


def reset_demo(db: Session, skip_confirm: bool = False) -> int:
    """Safely delete ONLY accounts listed in ALL_DEMO_EMAILS in FK order."""
    if not skip_confirm:
        try:
            confirm = (
                input("Are you sure you want to remove all demo accounts? [y/N]: ")
                .strip()
                .lower()
            )
            if confirm not in ("y", "yes"):
                print("Reset demo aborted by user.")
                return 0
        except (EOFError, KeyboardInterrupt):
            print("\nReset demo cancelled.")
            return 0

    demo_users = db.scalars(
        select(User.id).where(User.email.in_(ALL_DEMO_EMAILS))
    ).all()
    user_ids = list(demo_users)
    if not user_ids:
        print("No demo accounts found to remove.")
        return 0

    c_ids, a_ids, p_ids = _collect_demo_scope(db, user_ids)
    _delete_in_dependency_order(db, user_ids, c_ids, a_ids, p_ids)
    db.commit()
    print(
        f"Successfully deleted {len(user_ids)} demo user account(s) and dependent data."
    )
    return len(user_ids)
