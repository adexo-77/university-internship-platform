"""Clock provider for datetime operations."""

from collections.abc import Callable
from datetime import UTC, datetime

_clock: Callable[[], datetime] = lambda: datetime.now(UTC)


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
    _clock = lambda: datetime.now(UTC)
