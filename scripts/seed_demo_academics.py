"""Academic courses, assignments, and submissions demo seed helpers."""

from datetime import datetime, timedelta

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session


def seed_academics(db: Session, users: dict[str, User], now: datetime) -> None:
    inst, s1, s2 = users["inst"], users["s1"], users["s2"]
    c1 = db.scalar(
        select(Course).where(
            Course.instructor_id == inst.id, Course.title == "Web Architecture"
        )
    )
    if not c1:
        c1 = Course(
            instructor_id=inst.id,
            title="Web Architecture",
            description="Scalable web apps, async APIs, and distributed systems.",
            status=CourseStatus.PUBLISHED,
        )
        db.add(c1)
        db.flush()

    if not db.scalar(
        select(Course).where(
            Course.instructor_id == inst.id, Course.title == "Cloud DevOps"
        )
    ):
        db.add(
            Course(
                instructor_id=inst.id,
                title="Cloud DevOps",
                description="Draft course on Docker, Kubernetes, and CI pipelines.",
                status=CourseStatus.DRAFT,
            )
        )

    for s in (s1, s2):
        if not db.scalar(
            select(Enrollment).where(
                Enrollment.course_id == c1.id, Enrollment.student_id == s.id
            )
        ):
            db.add(Enrollment(course_id=c1.id, student_id=s.id))
    db.flush()

    a_specs = [
        ("Microservices Design", now + timedelta(days=2)),
        ("Capstone Project", now + timedelta(days=21)),
        ("Security & Auth", now - timedelta(days=4)),
    ]
    assignments: dict[str, Assignment] = {}
    for title, due in a_specs:
        a = db.scalar(
            select(Assignment).where(
                Assignment.course_id == c1.id, Assignment.title == title
            )
        )
        if not a:
            a = Assignment(
                course_id=c1.id,
                title=title,
                due_at=due,
                max_points=100,
                description=f"Task: {title}",
            )
            db.add(a)
            db.flush()
        assignments[title] = a

    sec_a = assignments["Security & Auth"]
    if not db.scalar(
        select(Submission).where(
            Submission.assignment_id == sec_a.id, Submission.student_id == s1.id
        )
    ):
        db.add(
            Submission(
                assignment_id=sec_a.id,
                student_id=s1.id,
                content="Comprehensive analysis of token hashing and CSRF defenses.",
                link_url="https://github.com/demo/security-audit",
                is_late=False,
                grade=95,
                feedback="Excellent work on defense in depth.",
                graded_at=now - timedelta(days=2),
                graded_by=inst.id,
            )
        )
    if not db.scalar(
        select(Submission).where(
            Submission.assignment_id == sec_a.id, Submission.student_id == s2.id
        )
    ):
        db.add(
            Submission(
                assignment_id=sec_a.id,
                student_id=s2.id,
                content="Late submission on authentication tokens.",
                link_url="https://github.com/demo2/late-auth",
                is_late=True,
            )
        )
    db.flush()
