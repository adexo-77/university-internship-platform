"""Clock provider for datetime operations."""

from collections.abc import Callable
from datetime import UTC, datetime


def _default_clock() -> datetime:
    return datetime.now(UTC)


_clock: Callable[[], datetime] = _default_clock


def get_now() -> datetime:
    """Return current UTC datetime."""
    return _clock()


def set_clock(clock_fn: Callable[[], datetime]) -> None:
    """Set custom clock function for test harnesses."""
    global _clock
    _clock = clock_fn


def reset_clock() -> None:
    """Reset clock function to system UTC."""
    global _clock
    _clock = _default_clock
