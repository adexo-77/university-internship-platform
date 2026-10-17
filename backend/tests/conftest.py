"""Pytest configuration and fixtures for backend testing."""

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.core.config import settings
from app.core.database import get_db
from app.main import app

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", settings.TEST_DATABASE_URL)


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
            conn.execute(text("TRUNCATE TABLE sessions, users RESTART IDENTITY CASCADE"))
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
