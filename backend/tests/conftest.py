"""Pytest configuration and fixtures for backend testing."""

import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from alembic.config import Config
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import require_roles
from app.core.security import hash_password
from app.main import app
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.user import User, UserRole

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", settings.TEST_DATABASE_URL)

# Attach a test-only route to verify role enforcement dependencies across test suites
role_test_router = APIRouter(prefix="/api/test-roles", tags=["test"])
require_admin_role = require_roles(UserRole.ADMIN)


@role_test_router.get("/admin-only")
def admin_only_endpoint(
    current_user: User = Depends(require_admin_role),
) -> dict[str, str]:
    return {"message": f"Welcome admin {current_user.full_name}"}


app.include_router(role_test_router)


@pytest.fixture(scope="session", autouse=True)
def run_migrations_on_test_db() -> None:
    """Build the schema by running Alembic migrations once per test session."""
    alembic_ini_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    cfg = Config(str(alembic_ini_path))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")


@pytest.fixture(autouse=True)
def clean_tables_between_tests() -> Generator[None, None, None]:
    """Clean the tables between tests to guarantee test isolation."""
    yield
    try:
        engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
        with engine.connect() as conn, conn.begin():
            conn.execute(
                text(
                    "TRUNCATE TABLE submissions, assignments, enrollments, courses, "
                    "student_profiles, organization_profiles, sessions, users "
                    "RESTART IDENTITY CASCADE"
                )
            )
        engine.dispose()
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine using TEST_DATABASE_URL."""
    engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture
def real_db_session() -> Generator[Session, None, None]:
    """Provide a real database session to seed or verify database state directly."""
    test_engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
    testing_session_local = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        test_engine.dispose()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture with default dependencies."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def real_db_client() -> Generator[TestClient, None, None]:
    """TestClient configured to execute against real database from TEST_DATABASE_URL."""
    test_engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
    testing_session_local = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock database session for unit testing health/db error and success paths."""
    mock = MagicMock(spec=Session)
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock.execute.return_value = mock_result
    return mock


@pytest.fixture
def client_with_mock_db(
    mock_db_session: MagicMock,
) -> Generator[TestClient, None, None]:
    """TestClient with database session overridden by mock returning success."""

    def override_get_db() -> Generator[MagicMock, None, None]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_failing_db() -> Generator[TestClient, None, None]:
    """TestClient with database session throwing an OperationalError."""
    from sqlalchemy.exc import OperationalError

    mock = MagicMock(spec=Session)
    mock.execute.side_effect = OperationalError("connection refused", {}, None)

    def override_get_db() -> Generator[MagicMock, None, None]:
        yield mock

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_test_user(
    db: Session,
    email: str,
    role: UserRole,
    password: str = "Password123!",
    full_name: str = "Test User",
) -> User:
    """Helper to seed a user directly in the test database."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_test_user(client: TestClient, email: str, password: str = "Password123!") -> None:
    """Helper to authenticate a test client via login endpoint."""
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def seed_course_and_assignment(
    db: Session,
    instructor: User,
    due_delta_days: int = 5,
    max_points: int = 100,
) -> tuple[Course, Assignment]:
    """Helper to seed a published course and assignment."""
    course = Course(
        instructor_id=instructor.id,
        title="Algorithms",
        description="Data structures & algos",
        status=CourseStatus.PUBLISHED,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    assignment = Assignment(
        course_id=course.id,
        title="Problem Set 1",
        description="Graph theory",
        due_at=datetime.now(UTC) + timedelta(days=due_delta_days),
        max_points=max_points,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return course, assignment
