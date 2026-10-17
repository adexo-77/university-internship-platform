"""Main FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

app = FastAPI(
    title="University Learning & Internship Platform API",
    description="Backend API for Brolf Tech University Learning & Internship Platform",
    version="0.1.0",
)

# Configure CORS
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
    )


# Mount routers under /api only
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
