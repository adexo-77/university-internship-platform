"""Pydantic schemas package."""

from app.schemas.auth import (
    LoginRequest,
    PublicRegisterRole,
    RegisterRequest,
    UserResponse,
)
from app.schemas.health import (
    DatabaseHealthResponse,
    ErrorDetailResponse,
    HealthResponse,
)
from app.schemas.organization_profile import (
    OrganizationProfileResponse,
    OrganizationProfileUpdateRequest,
)
from app.schemas.student_profile import (
    StudentProfileResponse,
    StudentProfileUpdateRequest,
)

__all__ = [
    "DatabaseHealthResponse",
    "ErrorDetailResponse",
    "HealthResponse",
    "LoginRequest",
    "OrganizationProfileResponse",
    "OrganizationProfileUpdateRequest",
    "PublicRegisterRole",
    "RegisterRequest",
    "StudentProfileResponse",
    "StudentProfileUpdateRequest",
    "UserResponse",
]
