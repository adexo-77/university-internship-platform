"""Thin HTTP endpoints for role dashboards."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.dashboard_admin import AdminDashboardResponse
from app.schemas.dashboard_instructor import InstructorDashboardResponse
from app.schemas.dashboard_organization import OrganizationDashboardResponse
from app.schemas.dashboard_student import StudentDashboardResponse
from app.services.dashboard_admin import get_admin_dashboard
from app.services.dashboard_instructor import get_instructor_dashboard
from app.services.dashboard_organization import get_organization_dashboard
from app.services.dashboard_student import get_student_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


require_student = require_roles(UserRole.STUDENT)
require_instructor = require_roles(UserRole.INSTRUCTOR)
require_organization = require_roles(UserRole.ORGANIZATION)
require_admin = require_roles(UserRole.ADMIN)


@router.get("/student", response_model=StudentDashboardResponse)
def student_dashboard(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentDashboardResponse:
    """Retrieve aggregated dashboard metrics for the authenticated student."""
    return get_student_dashboard(db, current_user.id)


@router.get("/instructor", response_model=InstructorDashboardResponse)
def instructor_dashboard(
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> InstructorDashboardResponse:
    """Retrieve aggregated dashboard metrics for the authenticated instructor."""
    return get_instructor_dashboard(db, current_user.id)


@router.get("/organization", response_model=OrganizationDashboardResponse)
def organization_dashboard(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> OrganizationDashboardResponse:
    """Retrieve aggregated dashboard metrics for the authenticated organization."""
    return get_organization_dashboard(db, current_user.id)


@router.get("/admin", response_model=AdminDashboardResponse)
def admin_dashboard(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminDashboardResponse:
    """Retrieve high-level platform activity metrics for administrators."""
    return get_admin_dashboard(db)
