"""Integration tests for course resource access, visibility, 404 rules, and cascade delete."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course, CourseStatus
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from tests.factories import create_test_user, login_test_user


def _seed_course(
    db: Session, instructor: User, status: CourseStatus = CourseStatus.PUBLISHED
) -> Course:
    course = Course(
        instructor_id=instructor.id,
        title="Distributed Systems",
        description="Core curriculum",
        status=status,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def _enroll_student(db: Session, course_id: int, student_id: int) -> None:
    db.add(Enrollment(course_id=course_id, student_id=student_id))
    db.commit()


def test_resource_creation_permissions(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Only owner instructor can create resources; non-owners, admins, students get 403."""
    inst1 = create_test_user(real_db_session, "inst1_cr@test.edu", UserRole.INSTRUCTOR)
    inst2 = create_test_user(real_db_session, "inst2_cr@test.edu", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "admin_cr@test.edu", UserRole.ADMIN)
    student = create_test_user(real_db_session, "stud_cr@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst1)

    payload = {
        "title": "Python Docs",
        "url": "https://docs.python.org/3/",
        "description": "Official docs",
    }

    # Student -> 403
    login_test_user(real_db_client, student.email)
    assert (
        real_db_client.post(f"/api/courses/{course.id}/resources", json=payload).status_code == 403
    )

    # Other instructor -> 403
    login_test_user(real_db_client, inst2.email)
    assert (
        real_db_client.post(f"/api/courses/{course.id}/resources", json=payload).status_code == 403
    )

    # Admin -> 403 (owner instructor only)
    login_test_user(real_db_client, admin.email)
    assert (
        real_db_client.post(f"/api/courses/{course.id}/resources", json=payload).status_code == 403
    )

    # Owner instructor -> 201
    login_test_user(real_db_client, inst1.email)
    res = real_db_client.post(f"/api/courses/{course.id}/resources", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Python Docs"
    assert data["url"] == "https://docs.python.org/3/"
    assert data["course_id"] == course.id

    # Non-existent course -> 404
    assert real_db_client.post("/api/courses/999999/resources", json=payload).status_code == 404


def test_resource_visibility_and_404_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Draft course or non-enrolled student gets 404; owner, admin, enrolled student get 200."""
    inst = create_test_user(real_db_session, "inst_vis@test.edu", UserRole.INSTRUCTOR)
    other_inst = create_test_user(real_db_session, "other_inst_vis@test.edu", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "admin_vis@test.edu", UserRole.ADMIN)
    org = create_test_user(real_db_session, "org_vis@test.edu", UserRole.ORGANIZATION)
    enrolled_stud = create_test_user(real_db_session, "enrolled_vis@test.edu", UserRole.STUDENT)
    other_stud = create_test_user(real_db_session, "other_vis@test.edu", UserRole.STUDENT)

    pub_course = _seed_course(real_db_session, inst, CourseStatus.PUBLISHED)
    draft_course = _seed_course(real_db_session, inst, CourseStatus.DRAFT)

    _enroll_student(real_db_session, pub_course.id, enrolled_stud.id)
    _enroll_student(real_db_session, draft_course.id, enrolled_stud.id)

    # Add resource to pub_course and draft_course
    login_test_user(real_db_client, inst.email)
    real_db_client.post(
        f"/api/courses/{pub_course.id}/resources",
        json={"title": "Pub Resource", "url": "https://pub.example.com"},
    )
    real_db_client.post(
        f"/api/courses/{draft_course.id}/resources",
        json={"title": "Draft Resource", "url": "https://draft.example.com"},
    )

    # 1. Owner instructor can view both published and draft
    login_test_user(real_db_client, inst.email)
    assert real_db_client.get(f"/api/courses/{pub_course.id}/resources").status_code == 200
    assert real_db_client.get(f"/api/courses/{draft_course.id}/resources").status_code == 200

    # 2. Admin can view both published and draft
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get(f"/api/courses/{pub_course.id}/resources").status_code == 200
    assert real_db_client.get(f"/api/courses/{draft_course.id}/resources").status_code == 200

    # 3. Enrolled student can view published course resources, but gets 404 for draft course
    login_test_user(real_db_client, enrolled_stud.email)
    res_pub = real_db_client.get(f"/api/courses/{pub_course.id}/resources")
    assert res_pub.status_code == 200
    assert len(res_pub.json()) == 1
    assert real_db_client.get(f"/api/courses/{draft_course.id}/resources").status_code == 404

    # 4. Non-enrolled student gets 404 for published and draft
    login_test_user(real_db_client, other_stud.email)
    assert real_db_client.get(f"/api/courses/{pub_course.id}/resources").status_code == 404
    assert real_db_client.get(f"/api/courses/{draft_course.id}/resources").status_code == 404

    # 5. Other instructor and organization get 404
    login_test_user(real_db_client, other_inst.email)
    assert real_db_client.get(f"/api/courses/{pub_course.id}/resources").status_code == 404
    login_test_user(real_db_client, org.email)
    assert real_db_client.get(f"/api/courses/{pub_course.id}/resources").status_code == 404


def test_resource_update_delete_and_cascade(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner can PATCH and DELETE; others get 403; deleting course cascades."""
    inst1 = create_test_user(real_db_session, "inst1_upd@test.edu", UserRole.INSTRUCTOR)
    inst2 = create_test_user(real_db_session, "inst2_upd@test.edu", UserRole.INSTRUCTOR)
    student = create_test_user(real_db_session, "stud_upd@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst1)

    login_test_user(real_db_client, inst1.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/resources",
        json={"title": "Original Title", "url": "https://orig.example.com", "description": "Orig"},
    )
    resource_id = res.json()["id"]

    # Student cannot patch or delete -> 403
    login_test_user(real_db_client, student.email)
    assert (
        real_db_client.patch(f"/api/resources/{resource_id}", json={"title": "Hack"}).status_code
        == 403
    )
    assert real_db_client.delete(f"/api/resources/{resource_id}").status_code == 403

    # Other instructor cannot patch or delete -> 403
    login_test_user(real_db_client, inst2.email)
    assert (
        real_db_client.patch(f"/api/resources/{resource_id}", json={"title": "Hack"}).status_code
        == 403
    )
    assert real_db_client.delete(f"/api/resources/{resource_id}").status_code == 403

    # Missing resource -> 404
    login_test_user(real_db_client, inst1.email)
    assert real_db_client.patch("/api/resources/999999", json={"title": "Test"}).status_code == 404
    assert real_db_client.delete("/api/resources/999999").status_code == 404

    # Owner patches title and url
    patch_res = real_db_client.patch(
        f"/api/resources/{resource_id}",
        json={"title": "Updated Title", "url": "https://updated.example.com"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Title"
    assert patch_res.json()["url"] == "https://updated.example.com"
    assert patch_res.json()["description"] == "Orig"

    # Cascade delete with course:
    # Add a second resource
    real_db_client.post(
        f"/api/courses/{course.id}/resources",
        json={"title": "Second Resource", "url": "https://second.example.com"},
    )
    count_before = real_db_session.scalar(
        select(CourseResource).where(CourseResource.course_id == course.id)
    )
    assert count_before is not None

    # Delete course from session
    c_obj = real_db_session.scalar(select(Course).where(Course.id == course.id))
    assert c_obj is not None
    real_db_session.delete(c_obj)
    real_db_session.commit()

    # Resources are cascade deleted
    remaining = real_db_session.scalars(
        select(CourseResource).where(CourseResource.course_id == course.id)
    ).all()
    assert len(remaining) == 0

    # Also test DELETE endpoint on a fresh resource
    course2 = _seed_course(real_db_session, inst1)
    res2 = real_db_client.post(
        f"/api/courses/{course2.id}/resources",
        json={"title": "To Delete", "url": "https://delete.example.com"},
    )
    r2_id = res2.json()["id"]
    del_res = real_db_client.delete(f"/api/resources/{r2_id}")
    assert del_res.status_code == 204
    assert real_db_session.scalar(select(CourseResource).where(CourseResource.id == r2_id)) is None
