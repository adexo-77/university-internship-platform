"""Course resources demo seed helpers."""

from app.models.course import Course
from app.models.course_resource import CourseResource
from sqlalchemy import select
from sqlalchemy.orm import Session

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


def seed_course_resources(db: Session, courses: dict[str, Course]) -> None:
    """Seed reference learning resources for published courses."""
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
