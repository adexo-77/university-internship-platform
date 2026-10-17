"""Authentication and authorization dependencies for FastAPI endpoints."""

from collections.abc import Callable

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import SESSION_COOKIE_NAME
from app.models.user import User, UserRole
from app.services.auth import AuthService


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Dependency that resolves the authenticated user from the session cookie.

    Raises:
        UnauthorizedException: If session cookie is missing, invalid, or expired.
    """
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not raw_token:
        raise UnauthorizedException("Authentication required")

    user = AuthService.resolve_current_user(db=db, raw_token=raw_token)
    if user is None:
        raise UnauthorizedException("Authentication required")

    return user


def require_roles(*roles: UserRole | str) -> Callable[[User], User]:
    """Factory creating a role-enforcement dependency.

    Enforces that the authenticated user possesses one of the authorized roles.
    Raises:
        ForbiddenException (403): If the user's role is not authorized.
    """
    allowed_roles = {r.value if isinstance(r, UserRole) else str(r) for r in roles}

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise ForbiddenException("Insufficient permissions to access this resource")
        return current_user

    return role_checker
