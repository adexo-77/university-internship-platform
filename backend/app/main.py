"""Main FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.csrf import CSRFMiddleware
from app.core.exceptions import AppException
from app.core.security_headers import SecurityHeadersMiddleware
from app.routers.admin_internship import router as admin_internship_router
from app.routers.admin_organization import router as admin_organization_router
from app.routers.admin_user import router as admin_user_router
from app.routers.application import router as application_router
from app.routers.assignment import router as assignment_router
from app.routers.auth import router as auth_router
from app.routers.course import router as course_router
from app.routers.dashboard import router as dashboard_router
from app.routers.enrollment import router as enrollment_router
from app.routers.health import router as health_router
from app.routers.internship import router as internship_router
from app.routers.organization_profile import router as organization_profile_router
from app.routers.student_profile import router as student_profile_router
from app.routers.submission import router as submission_router

app = FastAPI(
    title="University Learning & Internship Platform API",
    description="Backend API for Brolf Tech University Learning & Internship Platform",
    version="0.1.0",
)

# Configure Security Headers, CSRF & CORS
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Consistent error handler for domain application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code or "INTERNAL_ERROR"},
        headers=getattr(exc, "headers", None),
    )


# Mount routers under /api only
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(student_profile_router, prefix="/api")
app.include_router(organization_profile_router, prefix="/api")
app.include_router(course_router, prefix="/api")
app.include_router(enrollment_router, prefix="/api")
app.include_router(assignment_router, prefix="/api")
app.include_router(submission_router, prefix="/api")
app.include_router(internship_router, prefix="/api")
app.include_router(application_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")
app.include_router(admin_organization_router, prefix="/api")
app.include_router(admin_internship_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
