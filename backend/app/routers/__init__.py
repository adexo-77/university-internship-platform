"""API routers module."""

from app.routers.assignment import router as assignment_router
from app.routers.auth import router as auth_router
from app.routers.course import router as course_router
from app.routers.enrollment import router as enrollment_router
from app.routers.health import router as health_router
from app.routers.organization_profile import router as organization_profile_router
from app.routers.student_profile import router as student_profile_router
from app.routers.submission import router as submission_router

__all__ = [
    "assignment_router",
    "auth_router",
    "course_router",
    "enrollment_router",
    "health_router",
    "organization_profile_router",
    "student_profile_router",
    "submission_router",
]
