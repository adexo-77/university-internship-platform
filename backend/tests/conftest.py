"""Pytest configuration and fixtures for backend testing."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.main import app

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", settings.TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine using TEST_DATABASE_URL if available."""
    try:
        engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.close()
        yield engine
    except Exception:
        yield None


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
def client_with_mock_db(mock_db_session: MagicMock) -> Generator[TestClient, None, None]:
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
