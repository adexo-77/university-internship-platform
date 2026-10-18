"""Pydantic schemas package."""

from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.schemas.auth import (
    LoginRequest,
    PublicRegisterRole,
    RegisterRequest,
    UserResponse,
)
from app.schemas.course import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)
from app.schemas.enrollment import (
    EnrolledStudentResponse,
    EnrollmentActionResponse,
    EnrollmentResponse,
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
from app.schemas.submission import (
    StudentSubmissionRosterItem,
    SubmissionGrade,
    SubmissionResponse,
    SubmissionSubmit,
)

__all__ = [
    "AssignmentCreate",
    "AssignmentResponse",
    "AssignmentUpdate",
    "CourseCreate",
    "CourseListResponse",
    "CourseResponse",
    "CourseUpdate",
    "DatabaseHealthResponse",
    "EnrolledStudentResponse",
    "EnrollmentActionResponse",
    "EnrollmentResponse",
    "ErrorDetailResponse",
    "HealthResponse",
    "LoginRequest",
    "OrganizationProfileResponse",
    "OrganizationProfileUpdateRequest",
    "PublicRegisterRole",
    "RegisterRequest",
    "StudentProfileResponse",
    "StudentProfileUpdateRequest",
    "StudentSubmissionRosterItem",
    "SubmissionGrade",
    "SubmissionResponse",
    "SubmissionSubmit",
    "UserResponse",
]
