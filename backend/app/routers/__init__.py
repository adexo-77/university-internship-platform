"""API routers module."""

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.organization_profile import router as organization_profile_router
from app.routers.student_profile import router as student_profile_router

__all__ = [
    "auth_router",
    "health_router",
    "organization_profile_router",
    "student_profile_router",
]
