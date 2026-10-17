"""Health check service handling system and database availability logic."""

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseUnavailableException
from app.schemas.health import DatabaseHealthResponse, HealthResponse

logger = logging.getLogger(__name__)


class HealthService:
    """Service encapsulating health verification operations."""

    @staticmethod
    def get_system_health() -> HealthResponse:
        """Return the basic system availability status."""
        return HealthResponse(status="ok")

    @staticmethod
    def check_database_health(db: Session) -> DatabaseHealthResponse:
        """Execute a simple query to verify database connectivity and operational status."""
        try:
            result = db.execute(text("SELECT 1")).scalar()
            if result != 1:
                raise DatabaseUnavailableException("Unexpected response from database query.")
            return DatabaseHealthResponse(database="ok")
        except SQLAlchemyError as exc:
            logger.error("Database health check failed: %s", exc)
            raise DatabaseUnavailableException(f"Database connection error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected error during database health check: %s", exc)
            raise DatabaseUnavailableException(f"Unexpected database error: {exc}") from exc
