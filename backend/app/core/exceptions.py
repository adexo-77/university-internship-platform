"""Custom application exceptions with status code and machine-readable error codes."""


class AppException(Exception):
    """Base application exception with error code and HTTP status code."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        status_code: int = 500,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class DatabaseUnavailableException(AppException):
    """Raised when database query or connection check fails."""

    def __init__(
        self,
        message: str = "Database unavailable",
        code: str = "DATABASE_UNAVAILABLE",
    ) -> None:
        super().__init__(message=message, code=code, status_code=500)


class InvalidCredentialsException(AppException):
    """Raised on authentication failure (unknown user, bad password, inactive account)."""

    def __init__(
        self,
        message: str = "Invalid email or password",
        code: str = "INVALID_CREDENTIALS",
    ) -> None:
        super().__init__(message=message, code=code, status_code=401)


class EmailAlreadyExistsException(AppException):
    """Raised when registering an email that already exists."""

    def __init__(
        self,
        message: str = "An account with this email already exists",
        code: str = "EMAIL_ALREADY_REGISTERED",
    ) -> None:
        super().__init__(message=message, code=code, status_code=409)


class UnauthorizedException(AppException):
    """Raised when authentication is missing or session has expired."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(message=message, code=code, status_code=401)


class ForbiddenException(AppException):
    """Raised when an authenticated user lacks required role permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions to access this resource",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(message=message, code=code, status_code=403)


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(message=message, code=code, status_code=404)


class ConflictException(AppException):
    """Raised when an action conflicts with the current resource state."""

    def __init__(
        self,
        message: str = "Conflict with current state",
        code: str = "CONFLICT",
    ) -> None:
        super().__init__(message=message, code=code, status_code=409)
