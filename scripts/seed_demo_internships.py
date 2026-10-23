"""Internship postings and applications demo seed helpers."""

from datetime import datetime, timedelta

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session


def seed_internships_and_apps(
    db: Session, users: dict[str, User], now: datetime
) -> None:
    org, admin, s1, s2 = users["org"], users["admin"], users["s1"], users["s2"]
    p_specs = [
        (
            "Software Engineering Intern",
            InternshipStatus.OPEN,
            now + timedelta(days=30),
            None,
        ),
        ("UI/UX Design Intern", InternshipStatus.OPEN, now + timedelta(days=25), None),
        (
            "AI Research Intern",
            InternshipStatus.PENDING_REVIEW,
            now + timedelta(days=45),
            None,
        ),
        (
            "Cloud Systems Intern",
            InternshipStatus.DRAFT,
            now + timedelta(days=60),
            None,
        ),
        (
            "Crypto Trading Intern",
            InternshipStatus.REJECTED,
            now + timedelta(days=15),
            "Scope does not meet educational guidelines.",
        ),
        (
            "Systems Intern 2025",
            InternshipStatus.CLOSED,
            now - timedelta(days=10),
            None,
        ),
    ]
    postings: dict[str, Internship] = {}
    for title, st, dl, note in p_specs:
        p = db.scalar(
            select(Internship).where(
                Internship.organization_id == org.id, Internship.title == title
            )
        )
        if not p:
            p = Internship(
                organization_id=org.id,
                title=title,
                description=f"Role: {title}",
                requirements="Strong analytical and problem-solving skills.",
                location="San Francisco, CA",
                work_mode=InternshipWorkMode.REMOTE,
                duration_weeks=12,
                application_deadline=dl,
                status=st,
                review_note=note,
                reviewed_by=admin.id if note else None,
                reviewed_at=now - timedelta(days=2) if note else None,
            )
            db.add(p)
            db.flush()
        postings[title] = p

    p_swe, p_ui, p_closed = (
        postings["Software Engineering Intern"],
        postings["UI/UX Design Intern"],
        postings["Systems Intern 2025"],
    )
    app_specs = [
        (
            p_swe.id,
            s1.id,
            ApplicationStatus.ACCEPTED,
            "Excited to join!",
            "Welcome to our team!",
        ),
        (p_swe.id, s2.id, ApplicationStatus.SUBMITTED, "Applying for SWE role.", None),
        (
            p_ui.id,
            s1.id,
            ApplicationStatus.SHORTLISTED,
            "Portfolio attached.",
            "Shortlisted.",
        ),
        (
            p_ui.id,
            s2.id,
            ApplicationStatus.REJECTED,
            "Applying for UI role.",
            "Role filled.",
        ),
        (
            p_closed.id,
            s1.id,
            ApplicationStatus.WITHDRAWN,
            "Withdrawing application.",
            None,
        ),
    ]
    for pid, sid, st, cl, msg in app_specs:
        if not db.scalar(
            select(Application).where(
                Application.posting_id == pid, Application.student_id == sid
            )
        ):
            db.add(
                Application(
                    posting_id=pid,
                    student_id=sid,
                    cover_letter=cl,
                    status=st,
                    decision_message=msg,
                    decided_at=now - timedelta(days=1) if msg else None,
                )
            )
    db.flush()
