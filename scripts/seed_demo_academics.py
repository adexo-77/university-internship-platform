"""Academic courses, assignments, and submissions demo seed helpers."""

from datetime import datetime, timedelta

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session

COURSES_DATA = [
    (
        "inst1",
        "Introduction to Programming",
        "Foundations of procedural programming, algorithms, basic data structures, and problem-solving techniques using Python.",
        CourseStatus.PUBLISHED,
    ),
    (
        "inst1",
        "Database Systems",
        "Relational modeling, SQL querying, schema normalization, indexing, and transaction management with PostgreSQL.",
        CourseStatus.PUBLISHED,
    ),
    (
        "inst2",
        "Software Engineering",
        "Software development lifecycle, Agile methodologies, architectural patterns, automated testing, and CI/CD pipelines.",
        CourseStatus.DRAFT,
    ),
]


def _seed_courses(db: Session, users: dict[str, User]) -> dict[str, Course]:
    courses: dict[str, Course] = {}
    for inst_key, title, desc, status in COURSES_DATA:
        instructor = users[inst_key]
        c = db.scalar(
            select(Course).where(
                Course.instructor_id == instructor.id, Course.title == title
            )
        )
        if not c:
            c = Course(
                instructor_id=instructor.id,
                title=title,
                description=desc,
                status=status,
            )
            db.add(c)
            db.flush()
        courses[title] = c
    return courses


def _seed_enrollments(
    db: Session, courses: dict[str, Course], users: dict[str, User]
) -> None:
    c_db = courses["Database Systems"]
    c_prog = courses["Introduction to Programming"]
    for s_key in ("s1", "s2", "s3"):
        s = users[s_key]
        for course in (c_db, c_prog):
            if not db.scalar(
                select(Enrollment).where(
                    Enrollment.course_id == course.id, Enrollment.student_id == s.id
                )
            ):
                db.add(Enrollment(course_id=course.id, student_id=s.id))
    db.flush()


def _seed_assignments_and_submissions(
    db: Session, course: Course, users: dict[str, User], now: datetime
) -> None:
    specs = [
        (
            "Relational Schema Design & Normalization",
            now + timedelta(days=3),
            "Design a relational schema for a university clinic management system. Decompose all entities to Third Normal Form (3NF), specify primary/foreign keys, and submit table definitions.",
        ),
        (
            "Advanced SQL Queries & Index Optimization",
            now + timedelta(days=18),
            "Write analytical SQL queries using window functions and aggregations. Analyze query execution plans using EXPLAIN ANALYZE and suggest composite indexes.",
        ),
        (
            "ER Diagramming & Conceptual Modeling",
            now - timedelta(days=5),
            "Construct an Entity-Relationship (ER) diagram for a student registration system. Detail entity cardinalities, composite attributes, and weak entities.",
        ),
    ]
    assignments: dict[str, Assignment] = {}
    for title, due, desc in specs:
        a = db.scalar(
            select(Assignment).where(
                Assignment.course_id == course.id, Assignment.title == title
            )
        )
        if not a:
            a = Assignment(
                course_id=course.id,
                title=title,
                due_at=due,
                max_points=100,
                description=desc,
            )
            db.add(a)
            db.flush()
        assignments[title] = a

    er_a = assignments["ER Diagramming & Conceptual Modeling"]
    s1, s2, s3, inst1 = users["s1"], users["s2"], users["s3"], users["inst1"]

    subs = [
        (
            s1.id,
            "Complete Entity-Relationship diagram for university clinic management, mapped to 3NF tables with foreign keys and unique constraints.",
            "https://github.com/abeltesfaye/clinic-er-model",
            False,
            100,
            "Outstanding structural design and clear cardinalities.",
            now - timedelta(days=3),
        ),
        (
            s2.id,
            "Conceptual data model and normalization notes for student course registration portal.",
            "https://github.com/merongirma/course-reg-db",
            True,
            None,
            None,
            None,
        ),
        (
            s3.id,
            "Initial draft of the entity-relationship schema for registration entities.",
            "https://github.com/dawitlemma/er-draft",
            True,
            78,
            "Good effort on entity attributes. Be careful with foreign key definitions.",
            now - timedelta(days=1),
        ),
    ]
    for sid, content, link, is_late, grade, fb, grad_at in subs:
        if not db.scalar(
            select(Submission).where(
                Submission.assignment_id == er_a.id, Submission.student_id == sid
            )
        ):
            db.add(
                Submission(
                    assignment_id=er_a.id,
                    student_id=sid,
                    content=content,
                    link_url=link,
                    is_late=is_late,
                    grade=grade,
                    feedback=fb,
                    graded_at=grad_at,
                    graded_by=inst1.id if grade is not None else None,
                )
            )
    db.flush()


RESOURCE_SPECS = [
    (
        "Introduction to Programming",
        "Official Python Tutorial",
        "https://docs.python.org/3/tutorial/",
        "The official Python tutorial covering core syntax, data structures, and standard library fundamentals.",
    ),
    (
        "Introduction to Programming",
        "Think Python 2e",
        "https://greenteapress.com/wp/think-python-2e/",
        "Free introductory programming textbook focusing on algorithmic thinking and Python foundations.",
    ),
    (
        "Database Systems",
        "PostgreSQL Official Documentation",
        "https://www.postgresql.org/docs/current/",
        "Complete manual for PostgreSQL database server architecture, SQL syntax, and administration.",
    ),
    (
        "Database Systems",
        "Use The Index, Luke!",
        "https://use-the-index-luke.com/",
        "Guide to database indexing and SQL performance optimization for developers.",
    ),
    (
        "Software Engineering",
        "Refactoring Guru: Design Patterns",
        "https://refactoring.guru/design-patterns",
        "Visual guide to architectural and behavioral design patterns in modern software development.",
    ),
    (
        "Software Engineering",
        "Git Book Documentation",
        "https://git-scm.com/book/en/v2",
        "Pro Git official guide covering distributed version control workflows, branching, and collaboration.",
    ),
]


def _seed_course_resources(db: Session, courses: dict[str, Course]) -> None:
    for course_title, title, url, desc in RESOURCE_SPECS:
        course = courses.get(course_title)
        if not course:
            continue
        exists = db.scalar(
            select(CourseResource.id).where(
                CourseResource.course_id == course.id, CourseResource.title == title
            )
        )
        if not exists:
            db.add(
                CourseResource(
                    course_id=course.id, title=title, url=url, description=desc
                )
            )
    db.flush()


def seed_academics(db: Session, users: dict[str, User], now: datetime) -> None:
    courses = _seed_courses(db, users)
    _seed_enrollments(db, courses, users)
    _seed_course_resources(db, courses)
    _seed_assignments_and_submissions(db, courses["Database Systems"], users, now)
