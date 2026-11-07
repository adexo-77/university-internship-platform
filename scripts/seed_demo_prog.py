"""Intro to programming demo assignments and submissions seed helper."""

from datetime import datetime, timedelta

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.submission import Submission
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session

PROG_SPECS = [
    (
        "Python Basics & Control Flow Lab",
        -timedelta(days=1),
        25,
        "Implement basic Python control structures, functions, and unit tests.",
    ),
    (
        "Data Structures & Algorithm Complexity Project",
        timedelta(days=1),
        80,
        "Implement sorting and search algorithms with computational complexity analysis.",
    ),
    (
        "Object-Oriented Programming Workshop",
        timedelta(days=14),
        100,
        "Design Python class hierarchies with encapsulation, inheritance, and test coverage.",
    ),
]


def seed_programming_assignments(
    db: Session, course: Course, users: dict[str, User], now: datetime
) -> None:
    """Seed additive programming assignments for realistic study-plan scenarios."""
    assignments: dict[str, Assignment] = {}
    for title, delta, pts, desc in PROG_SPECS:
        a = db.scalar(
            select(Assignment).where(
                Assignment.course_id == course.id, Assignment.title == title
            )
        )
        if not a:
            a = Assignment(
                course_id=course.id,
                title=title,
                due_at=now + delta,
                max_points=pts,
                description=desc,
            )
            db.add(a)
            db.flush()
        else:
            a.due_at = now + delta
            a.max_points = pts
            a.description = desc
        assignments[title] = a

    lab_a = assignments["Python Basics & Control Flow Lab"]
    algo_a = assignments["Data Structures & Algorithm Complexity Project"]
    s2 = users["s2"]

    subs = [
        (
            lab_a.id,
            s2.id,
            "Control flow structures and unit test implementations in Python.",
            "https://github.com/merongirma/python-control-flow",
        ),
        (
            algo_a.id,
            s2.id,
            "Benchmarking algorithm complexity notes and sorting implementations.",
            "https://github.com/merongirma/algo-complexity",
        ),
    ]
    for aid, sid, content, link in subs:
        existing = db.scalar(
            select(Submission).where(
                Submission.assignment_id == aid, Submission.student_id == sid
            )
        )
        if not existing:
            db.add(
                Submission(
                    assignment_id=aid,
                    student_id=sid,
                    content=content,
                    link_url=link,
                    is_late=False,
                    grade=None,
                    feedback=None,
                    graded_at=None,
                    graded_by=None,
                )
            )
        else:
            existing.content = content
            existing.link_url = link
    db.flush()
