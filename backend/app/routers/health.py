"""Health check routers."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import DatabaseUnavailableException
from app.schemas.health import DatabaseHealthResponse, ErrorDetailResponse, HealthResponse
from app.services.health import HealthService

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health Check",
    description="Returns the operational status of the API server.",
)
def get_health() -> HealthResponse:
    """Return system operational status."""
    return HealthService.get_system_health()


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorDetailResponse,
            "description": "Database connection or query failed",
        }
    },
    summary="Database Health Check",
    description="Executes a test query to verify PostgreSQL database connectivity.",
)
def get_database_health(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """Verify database connectivity."""
    try:
        return HealthService.check_database_health(db)
    except DatabaseUnavailableException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
