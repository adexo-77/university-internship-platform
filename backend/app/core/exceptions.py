"""Custom application exceptions."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class DatabaseUnavailableException(AppException):
    """Raised when database query or connection check fails."""

    def __init__(
        self, message: str = "Database unavailable", code: str = "DATABASE_UNAVAILABLE"
    ) -> None:
        super().__init__(message=message, code=code)
