"""Authentication API router handling registration, login, logout, and user identity."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import get_client_ip
from app.core.security import SESSION_COOKIE_NAME, SESSION_LIFETIME_SECONDS
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, raw_token: str) -> None:
    """Attach secure session cookie to HTTP response."""
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=raw_token,
        max_age=SESSION_LIFETIME_SECONDS,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    """Clear session cookie from HTTP response."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register new user account",
)
def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    """Register student or organization account and establish an authenticated session."""
    client_ip = get_client_ip(request)
    user, raw_token = AuthService.register(db=db, request=payload, client_ip=client_ip)
    _set_auth_cookie(response=response, raw_token=raw_token)
    return user


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Authenticate user credentials",
)
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    """Verify user credentials and establish an authenticated session."""
    client_ip = get_client_ip(request)
    user, raw_token = AuthService.authenticate(db=db, request=payload, client_ip=client_ip)
    _set_auth_cookie(response=response, raw_token=raw_token)
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Terminate session",
)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Invalidate session in database and clear session cookie."""
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    AuthService.delete_session(db=db, raw_token=raw_token)
    _clear_auth_cookie(response=response)
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get current user identity",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return identity and profile of currently authenticated user."""
    return current_user


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Change authenticated user password and invalidate all other sessions."""
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    AuthService.change_password(
        db=db,
        user=current_user,
        current_token=raw_token,
        request=payload,
    )
    return {"message": "Password changed successfully"}
