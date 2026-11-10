"""Injectable clock provider for deterministic datetime operations."""

import os
from datetime import UTC, datetime


def get_now() -> datetime:
    """Return current UTC datetime, defaulting to TEST_FROZEN_NOW when set."""
    env_now = os.environ.get("TEST_FROZEN_NOW")
    if env_now:
        dt = datetime.fromisoformat(env_now)
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
    return datetime.now(UTC)
