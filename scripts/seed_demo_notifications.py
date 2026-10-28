"""Idempotent notification seeder for demo accounts using real seeded objects."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.internship import Internship
from app.models.notification import Notification, NotificationKind
from app.models.organization_profile import OrganizationProfile
from app.models.submission import Submission
from app.models.user import User


def seed_notifications(db: Session, users: dict[str, User], now: datetime) -> int:
    """Seed realistic initial notifications for demo accounts idempotently."""
    created_count = 0

    s1 = users.get("s1") or users.get("abel.tesfaye@example.com")
    s2 = users.get("s2") or users.get("meron.girma@example.com")
    inst1 = users.get("inst1") or users.get("tadesse.bekele@example.com")
    org1 = users.get("org1") or users.get("yohannes.haile@example.com")
    org3 = users.get("org3") or users.get("eyob.kassa@example.com")
    admin = users.get("admin") or users.get("mulugeta.assefa@example.com")
    coord = users.get("coord") or users.get("selamawit.tadesse@example.com")

    # Fetch real entities
    er_a = db.scalar(
        select(Assignment).where(
            Assignment.title == "ER Diagramming & Conceptual Modeling"
        )
    )
    rel_a = db.scalar(
        select(Assignment).where(
            Assignment.title == "Relational Schema Design & Normalization"
        )
    )
    course_db = db.scalar(
        select(Course).where(Course.title == "Database Systems")
    )

    p_web = db.scalar(
        select(Internship).where(Internship.title == "Junior Web Developer Intern")
    )
    p_mobile = db.scalar(
        select(Internship).where(Internship.title == "Mobile Application Intern")
    )

    sub_abel = (
        db.scalar(
            select(Submission).where(
                Submission.assignment_id == er_a.id,
                Submission.student_id == s1.id,
            )
        )
        if er_a and s1
        else None
    )
    sub_meron = (
        db.scalar(
            select(Submission).where(
                Submission.assignment_id == er_a.id,
                Submission.student_id == s2.id,
            )
        )
        if er_a and s2
        else None
    )

    app_abel = (
        db.scalar(
            select(Application).where(
                Application.posting_id == p_web.id,
                Application.student_id == s1.id,
            )
        )
        if p_web and s1
        else None
    )
    app_meron = (
        db.scalar(
            select(Application).where(
                Application.posting_id == p_web.id,
                Application.student_id == s2.id,
            )
        )
        if p_web and s2
        else None
    )

    op_abay = (
        db.scalar(
            select(OrganizationProfile).where(OrganizationProfile.user_id == org3.id)
        )
        if org3
        else None
    )

    demo_specs: list[tuple[User, NotificationKind, str, str, str, datetime | None]] = []

    # Abel Tesfaye
    if s1 and er_a and sub_abel:
        demo_specs.append(
            (
                s1,
                NotificationKind.SUBMISSION_GRADED,
                f"Assignment graded: {er_a.title} ({sub_abel.grade}/{er_a.max_points})",
                f"Your submission for '{er_a.title}' was graded: {sub_abel.grade}/{er_a.max_points}.",
                f"/assignments/{er_a.id}",
                now - timedelta(days=1),
            )
        )
    if s1 and p_web and app_abel:
        demo_specs.append(
            (
                s1,
                NotificationKind.APPLICATION_DECISION,
                f"Application accepted: {p_web.title}",
                f"Your application for '{p_web.title}' was marked as accepted: {app_abel.decision_message}",
                f"/applications/{app_abel.id}",
                None,
            )
        )
    if s1 and rel_a and course_db:
        demo_specs.append(
            (
                s1,
                NotificationKind.ASSIGNMENT_CREATED,
                f"New Assignment: {rel_a.title}",
                f"A new assignment '{rel_a.title}' was posted in '{course_db.title}'.",
                f"/assignments/{rel_a.id}",
                None,
            )
        )

    # Meron Girma
    if s2 and p_web and app_meron:
        demo_specs.append(
            (
                s2,
                NotificationKind.APPLICATION_DECISION,
                f"Application shortlisted: {p_web.title}",
                f"Your application for '{p_web.title}' was marked as shortlisted: {app_meron.decision_message}",
                f"/applications/{app_meron.id}",
                None,
            )
        )

    # Dr. Tadesse Bekele
    if inst1 and er_a and s2 and sub_meron:
        demo_specs.append(
            (
                inst1,
                NotificationKind.FIRST_SUBMISSION,
                f"First submission: {er_a.title}",
                f"{s2.full_name} submitted the first response for '{er_a.title}'.",
                f"/assignments/{er_a.id}",
                None,
            )
        )

    # Yohannes Haile (Kaffa Digital Solutions)
    if org1 and p_web:
        demo_specs.extend(
            [
                (
                    org1,
                    NotificationKind.APPLICATION_RECEIVED,
                    f"New Application: {p_web.title}",
                    f"A new application was received for '{p_web.title}'.",
                    f"/internships/{p_web.id}",
                    None,
                ),
                (
                    org1,
                    NotificationKind.INTERNSHIP_STATUS,
                    f"Posting Approved: {p_web.title}",
                    f"Your posting '{p_web.title}' was approved.",
                    f"/internships/{p_web.id}",
                    now - timedelta(days=2),
                ),
                (
                    org1,
                    NotificationKind.ORGANIZATION_STATUS,
                    "Organization Account Approved",
                    "Your organization profile was reviewed and approved by an administrator.",
                    "/profile",
                    now - timedelta(days=3),
                ),
            ]
        )

    # Reviewers (Admin Dr. Mulugeta & Coordinator Ms. Selamawit)
    reviewers = [u for u in (admin, coord) if u is not None]
    for reviewer in reviewers:
        if op_abay:
            demo_specs.append(
                (
                    reviewer,
                    NotificationKind.ORGANIZATION_REGISTERED,
                    f"New Organization: {op_abay.organization_name}",
                    f"Organization '{op_abay.organization_name}' registered and is pending approval.",
                    "/admin/organizations",
                    None,
                )
            )
        if p_mobile:
            demo_specs.append(
                (
                    reviewer,
                    NotificationKind.INTERNSHIP_SUBMITTED,
                    f"Internship Review: {p_mobile.title}",
                    f"Internship '{p_mobile.title}' was submitted for review.",
                    "/admin/internship-reviews",
                    None,
                )
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
