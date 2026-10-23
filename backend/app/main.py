import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, OperationalError

from app.core.config import settings, validate_production_configuration
from app.core.csrf import CSRFMiddleware
from app.core.database import SessionLocal
from app.core.exceptions import AppException
from app.core.logging import RequestLoggingMiddleware, logger
from app.core.request_size import RequestSizeLimitMiddleware
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
from app.services.auth import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Execute startup security validation and session maintenance."""
    validate_production_configuration(settings)
    try:
        with SessionLocal() as db:
            AuthService.purge_expired_sessions(db)
    except Exception:
        pass
    yield


app = FastAPI(
    title="University Learning & Internship Platform API",
    description="Backend API for Brolf Tech University Learning & Internship Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure Logging, Request Size, Security Headers, CSRF & CORS
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
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


@app.exception_handler(OperationalError)
@app.exception_handler(DBAPIError)
async def database_unavailable_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return 503 with a clear message and request id when database is unavailable."""
    request_id = getattr(request.state, "request_id", None) or uuid.uuid4().hex
    logger.error(
        "request_id=%s method=%s path=%s status=503 database_unavailable error=%s",
        request_id,
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database service is temporarily unavailable. Please try again later.",
            "code": "DATABASE_UNAVAILABLE",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, _: Exception) -> JSONResponse:
    """Return generic JSON 500 with request id and never leak stack traces."""
    request_id = getattr(request.state, "request_id", None) or uuid.uuid4().hex
    logger.error(
        "request_id=%s method=%s path=%s status=500 unhandled_exception",
        request_id,
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "code": "INTERNAL_SERVER_ERROR",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
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
