"""Idempotent notification seeder for demo accounts."""

from datetime import datetime, timedelta

from app.models.notification import Notification, NotificationKind
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session


def seed_notifications(db: Session, users: dict[str, User], now: datetime) -> int:
    """Seed realistic initial notifications for demo accounts idempotently."""
    created_count = 0
    demo_specs: list[tuple[User, NotificationKind, str, str, str, datetime | None]] = []

    # Student demo accounts
    student = users.get("s1") or users.get("hana.worku@example.com")
    if student:
        demo_specs.extend(
            [
                (
                    student,
                    NotificationKind.ASSIGNMENT_CREATED,
                    "New Assignment: Distributed Consensus Lab",
                    "A new assignment 'Distributed Consensus Lab' was posted in your course.",
                    "/my-courses",
                    None,
                ),
                (
                    student,
                    NotificationKind.SUBMISSION_GRADED,
                    "Assignment Graded: Midterm Exam (92/100)",
                    "Your submission for 'Midterm Exam' has been graded: 92/100.",
                    "/my-courses",
                    now - timedelta(days=1),
                ),
                (
                    student,
                    NotificationKind.APPLICATION_DECISION,
                    "Application Shortlisted: Cloud Engineering Intern",
                    "Your application for 'Cloud Engineering Intern' has been shortlisted.",
                    "/my-applications",
                    None,
                ),
            ]
        )

    # Instructor demo accounts
    instructor = users.get("inst") or users.get("tadesse.bekele@example.com")
    if instructor:
        demo_specs.append(
            (
                instructor,
                NotificationKind.FIRST_SUBMISSION,
                "First Submission Received: Lab 1",
                "A student submitted the first response for 'Lab 1'.",
                "/my-courses",
                None,
            )
        )

    # Organization demo accounts
    org = users.get("org") or users.get("meron.girma@example.com")
    if org:
        demo_specs.extend(
            [
                (
                    org,
                    NotificationKind.APPLICATION_RECEIVED,
                    "New Application: Cloud Engineering Intern",
                    "A student submitted an application for Cloud Engineering Intern.",
                    "/my-internships",
                    None,
                ),
                (
                    org,
                    NotificationKind.INTERNSHIP_STATUS,
                    "Internship Approved: Cloud Engineering Intern",
                    "Your internship posting is approved and published in the catalogue.",
                    "/my-internships",
                    now - timedelta(days=2),
                ),
                (
                    org,
                    NotificationKind.ORGANIZATION_STATUS,
                    "Organization Account Approved",
                    "Your organization profile was reviewed and approved by an administrator.",
                    "/profile",
                    now - timedelta(days=3),
                ),
            ]
        )

    # Admin demo accounts
    admin = users.get("admin") or users.get("mulugeta.assefa@example.com")
    if admin:
        demo_specs.extend(
            [
                (
                    admin,
                    NotificationKind.ORGANIZATION_REGISTERED,
                    "New Organization Registration Pending",
                    "A new organization has registered and requires approval.",
                    "/admin/organizations",
                    None,
                ),
                (
                    admin,
                    NotificationKind.INTERNSHIP_SUBMITTED,
                    "Internship Review Queue Updated",
                    "An organization submitted an internship posting for admin review.",
                    "/admin/internship-reviews",
                    None,
                ),
            ]
        )

    for user_obj, kind, title, message, link, read_at in demo_specs:
        existing = db.scalar(
            select(Notification.id).where(
                Notification.user_id == user_obj.id,
                Notification.kind == kind,
                Notification.title == title,
            )
        )
        if existing is None:
            db.add(
                Notification(
                    user_id=user_obj.id,
                    kind=kind,
                    title=title,
                    message=message,
                    link_path=link,
                    read_at=read_at,
                    created_at=read_at or now,
                )
            )
            created_count += 1

    return created_count
