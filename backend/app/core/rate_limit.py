"""In-memory sliding-window rate limiter with an injectable clock.

NOTE: This in-memory implementation is intended for single-instance deployments.
Multi-instance deployments require a centralized shared store (e.g. Redis or Memcached).
"""

import math
import time
from collections.abc import Callable

from fastapi import Request

from app.core.config import settings
from app.core.exceptions import RateLimitExceededException


def get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting TRUSTED_PROXY configuration."""
    if settings.TRUSTED_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
            if ip:
                return ip
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


class RateLimiter:
    """Sliding-window rate limiter storing request timestamps in memory."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self.clock: Callable[[], float] = clock
        self.enabled: bool = settings.RATE_LIMIT_ENABLED
        self._store: dict[str, list[float]] = {}

    def reset(self) -> None:
        """Clear all stored rate limit history."""
        self._store.clear()

    def set_clock(self, clock: Callable[[], float]) -> None:
        """Inject a controllable clock for deterministic testing."""
        self.clock = clock

    def _prune_and_get(self, key: str, window: int) -> list[float]:
        now = self.clock()
        cutoff = now - window
        timestamps = [t for t in self._store.get(key, []) if t > cutoff]
        self._store[key] = timestamps
        return timestamps

    def _check_limit(self, key: str, limit: int, window: int) -> None:
        if not self.enabled:
            return
        timestamps = self._prune_and_get(key, window)
        if len(timestamps) >= limit:
            now = self.clock()
            earliest = timestamps[0]
            retry_after = max(1, math.ceil(earliest + window - now))
            raise RateLimitExceededException(retry_after=retry_after)

    def _record(self, key: str, window: int) -> None:
        if not self.enabled:
            return
        timestamps = self._prune_and_get(key, window)
        timestamps.append(self.clock())
        self._store[key] = timestamps

    def check_login_attempt(self, client_ip: str, email: str) -> None:
        """Verify IP attempt rate and (IP + email) failure rate before authentication."""
        if not self.enabled:
            return
        # 1. Check IP total attempt limit
        self._check_limit(
            key=f"login_ip:{client_ip}",
            limit=settings.RATE_LIMIT_LOGIN_IP_LIMIT,
            window=settings.RATE_LIMIT_LOGIN_IP_WINDOW,
        )
        # 2. Check (IP + email) failed attempts limit
        email_key = email.strip().lower()
        self._check_limit(
            key=f"login_fail:{client_ip}:{email_key}",
            limit=settings.RATE_LIMIT_LOGIN_FAIL_LIMIT,
            window=settings.RATE_LIMIT_LOGIN_FAIL_WINDOW,
        )
        # Record the IP-level attempt
        self._record(
            key=f"login_ip:{client_ip}",
            window=settings.RATE_LIMIT_LOGIN_IP_WINDOW,
        )

    def record_login_failure(self, client_ip: str, email: str) -> None:
        """Record a failed login attempt for (client IP + email)."""
        if not self.enabled:
            return
        email_key = email.strip().lower()
        self._record(
            key=f"login_fail:{client_ip}:{email_key}",
            window=settings.RATE_LIMIT_LOGIN_FAIL_WINDOW,
        )

    def reset_login_failures(self, client_ip: str, email: str) -> None:
        """Reset failed login count for (client IP + email) on successful login."""
        email_key = email.strip().lower()
        self._store.pop(f"login_fail:{client_ip}:{email_key}", None)

    def check_and_record_register(self, client_ip: str) -> None:
        """Enforce rate limits on registration per IP."""
        if not self.enabled:
            return
        key = f"register_ip:{client_ip}"
        self._check_limit(
            key=key,
            limit=settings.RATE_LIMIT_REGISTER_LIMIT,
            window=settings.RATE_LIMIT_REGISTER_WINDOW,
        )
        self._record(key=key, window=settings.RATE_LIMIT_REGISTER_WINDOW)

    def check_and_record_change_password(self, user_id: int) -> None:
        """Enforce rate limits on password changes per user."""
        if not self.enabled:
            return
        key = f"change_password_user:{user_id}"
        self._check_limit(
            key=key,
            limit=settings.RATE_LIMIT_CHANGE_PASSWORD_LIMIT,
            window=settings.RATE_LIMIT_CHANGE_PASSWORD_WINDOW,
        )
        self._record(key=key, window=settings.RATE_LIMIT_CHANGE_PASSWORD_WINDOW)


rate_limiter = RateLimiter()
