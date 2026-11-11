"""Boundary and algorithmic verification for rule-based study plan generation."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.clock import get_now
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_study_plan_overdue_and_due_today_boundaries(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Overdue coursework comes first and is flagged; work due today is flagged tight."""
    student = create_test_user(real_db_session, "stu_b@test.edu", UserRole.STUDENT)
    instructor = create_test_user(real_db_session, "inst_b@test.edu", UserRole.INSTRUCTOR)
    course = Course(
        instructor_id=instructor.id,
        title="Operating Systems",
        description="Core systems concepts",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(student_id=student.id, course_id=course.id))
    now = get_now()

    real_db_session.add_all(
        [
            Assignment(
                course_id=course.id,
                title="Lab 1: Shell",
                description="Build a unix shell",
                due_at=now - timedelta(days=2),
                max_points=15,
            ),
            Assignment(
                course_id=course.id,
                title="Lab 2: Threads",
                description="Thread sync",
                due_at=now + timedelta(hours=2),
                max_points=30,
            ),
            Assignment(
                course_id=course.id,
                title="Lab 3: Virtual Memory",
                description="Paging and TLB",
                due_at=now + timedelta(days=5),
                max_points=10,
            ),
        ]
    )
    real_db_session.commit()

    login_test_user(real_db_client, "stu_b@test.edu")
    resp = real_db_client.get("/api/students/me/study-plan?days=7")
    assert resp.status_code == 200
    data = resp.json()

    # Assert overdue list has a_overdue
    assert len(data["overdue"]) == 1
    assert data["overdue"][0]["title"] == "Lab 1: Shell"
    assert "overdue" in data["overdue"][0]["flags"]

    # Assert tight list has a_today
    tight_titles = [t["title"] for t in data["tight"]]
    assert "Lab 2: Threads" in tight_titles

    # Day 0 (today) should contain overdue task first, then today's task
    today_items = data["plan"][0]["items"]
    assert len(today_items) >= 2
    assert today_items[0]["title"] == "Lab 1: Shell"
    assert "overdue" in today_items[0]["flags"]
    assert today_items[1]["title"] == "Lab 2: Threads"
    assert "tight" in today_items[1]["flags"]


def test_study_plan_due_tomorrow_large_effort_tight_and_cap(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Assignment due tomorrow with >50 points (150m) exceeds today's 120m cap and is tight."""
    student = create_test_user(
        db=real_db_session, email="stu_plan_tight@example.com", role=UserRole.STUDENT
    )
    instructor = create_test_user(
        db=real_db_session, email="inst_plan_tight@example.com", role=UserRole.INSTRUCTOR
    )
    course = Course(
        instructor_id=instructor.id,
        title="Compiler Design",
        description="Lexing, parsing, and IR",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(student_id=student.id, course_id=course.id))

    now = get_now()
    # Assignment due tomorrow: max 80 points (>50 -> 150 min effort)
    # Capacity before tomorrow is only today (120 min). 150 > 120 => tight!
    real_db_session.add(
        Assignment(
            course_id=course.id,
            title="Project 1: Parser",
            description="Recursive descent parser",
            due_at=now + timedelta(days=1, hours=2),
            max_points=80,
        )
    )
    real_db_session.commit()

    login_test_user(real_db_client, "stu_plan_tight@example.com")
    resp = real_db_client.get("/api/students/me/study-plan?days=7")
    assert resp.status_code == 200
    data = resp.json()

    # Must be in tight list
    assert any(t["title"] == "Project 1: Parser" for t in data["tight"])

    # Scheduled 120 min today (day 0) and 30 min tomorrow (day 1, due date)
    day_0 = data["plan"][0]
    day_1 = data["plan"][1]
    day_0_tasks = [i for i in day_0["items"] if i["title"] == "Project 1: Parser"]
    day_1_tasks = [i for i in day_1["items"] if i["title"] == "Project 1: Parser"]

    assert len(day_0_tasks) == 1
    assert day_0_tasks[0]["suggested_minutes"] == 120
    assert "tight" in day_0_tasks[0]["flags"]

    assert len(day_1_tasks) == 1
    assert day_1_tasks[0]["suggested_minutes"] == 30
    assert "tight" in day_1_tasks[0]["flags"]

    # Nothing scheduled after due date
    for future_day in data["plan"][2:]:
        assert not any(i["title"] == "Project 1: Parser" for i in future_day["items"])


def test_study_plan_ordering_ties_and_submission_exclusion(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Equal deadline and points break ties by ID; submitted/graded work is excluded."""
    student = create_test_user(
        db=real_db_session, email="stu_plan_ties@example.com", role=UserRole.STUDENT
    )
    instructor = create_test_user(
        db=real_db_session, email="inst_plan_ties@example.com", role=UserRole.INSTRUCTOR
    )
    course = Course(
        instructor_id=instructor.id,
        title="Database Systems",
        description="Relational engines",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(student_id=student.id, course_id=course.id))

    common_due = get_now() + timedelta(days=4)
    a1 = Assignment(
        course_id=course.id,
        title="Assignment Beta",
        description="Optimization",
        due_at=common_due,
        max_points=50,
    )
    a2 = Assignment(
        course_id=course.id,
        title="Assignment Alpha",
        description="Indexing",
        due_at=common_due,
        max_points=50,
    )
    a_graded = Assignment(
        course_id=course.id,
        title="Assignment Graded",
        description="Storage",
        due_at=common_due,
        max_points=50,
    )
    real_db_session.add_all([a1, a2, a_graded])
    real_db_session.commit()

    # Student has submitted a_graded (with a grade)
    sub = Submission(
        assignment_id=a_graded.id,
        student_id=student.id,
        content="Solution submission",
        link_url="https://github.com/student/db-project",
        grade=45.0,
        graded_at=get_now(),
    )
    real_db_session.add(sub)
    real_db_session.commit()

    login_test_user(real_db_client, "stu_plan_ties@example.com")
    resp = real_db_client.get("/api/students/me/study-plan?days=7")
    assert resp.status_code == 200
    data = resp.json()

    # a_graded must be completely excluded
    all_titles = [i["title"] for day in data["plan"] for i in day["items"]]
    assert "Assignment Graded" not in all_titles

    # Verify ID ordering between a1 and a2 (a1 was created first, lower ID)
    assert a1.id < a2.id
    d0_items = [i["title"] for i in data["plan"][0]["items"]]
    assert d0_items.index("Assignment Beta") < d0_items.index("Assignment Alpha")


def test_study_plan_nothing_pending_and_student_without_courses(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Nothing pending says schedule clear; student with no courses gets enrolled notice."""
    create_test_user(
        db=real_db_session,
        email="stu_plan_clean@example.com",
        role=UserRole.STUDENT,
    )
    login_test_user(real_db_client, "stu_plan_clean@example.com")
    resp_no_courses = real_db_client.get("/api/students/me/study-plan")
    assert resp_no_courses.status_code == 200
    data_no_courses = resp_no_courses.json()
    sents = " ".join(data_no_courses["summary"]["sentences"])
    assert "You are not currently enrolled in any published courses." in sents
    assert "There is nothing pending to do right now" in sents
    assert data_no_courses["summary"]["metrics"]["enrolled_courses_count"] == 0
    assert data_no_courses["summary"]["metrics"]["assignments_due_count"] == 0
