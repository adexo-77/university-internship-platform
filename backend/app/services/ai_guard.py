"""AI guard layer: kill switch, consent, daily DB quotas, cache, caps, and output sanitizer."""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import OrderedDict
from collections.abc import Callable
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.clock import get_now
from app.core.config import Settings, settings
from app.core.exceptions import AppException, ForbiddenException, RateLimitExceededException
from app.models.ai_usage_daily import AiUsageDaily
from app.models.user import User
from app.services.ai_provider import AIProvider, AIProviderError, get_ai_provider

logger = logging.getLogger("app.ai")

MAX_SYSTEM_PROMPT_CHARS = 2000
MAX_USER_PROMPT_CHARS = 4000
MAX_OUTPUT_CHARS = 2000
MAX_CACHE_ENTRIES = 256

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_RESPONSE_CACHE: OrderedDict[str, tuple[datetime, str]] = OrderedDict()


class AIDisabledException(AppException):
    """Raised when AI assistance is disabled by the global kill switch."""

    def __init__(self) -> None:
        super().__init__(
            message="AI assistance is currently disabled.",
            code="AI_DISABLED",
            status_code=503,
        )


def clear_ai_cache() -> None:
    """Clear the in-memory AI response cache."""
    _RESPONSE_CACHE.clear()


def sanitize_ai_output(raw_text: str, max_chars: int = MAX_OUTPUT_CHARS) -> str:
    """Strip control characters, normalize newlines, and cap plain-text output length."""
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _CONTROL_CHARS_RE.sub("", normalized).strip()
    if len(cleaned) > max_chars:
        return cleaned[:max_chars].rstrip()
    return cleaned


def _cache_key(feature: str, system: str, user: str, max_tokens: int) -> str:
    raw = f"{feature}\n{max_tokens}\n{system}\n{user}".encode()
    return hashlib.sha256(raw).hexdigest()


def _get_cached(key: str, now: datetime) -> str | None:
    entry = _RESPONSE_CACHE.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if now >= expires_at:
        _RESPONSE_CACHE.pop(key, None)
        return None
    _RESPONSE_CACHE.move_to_end(key)
    return value


def _put_cached(key: str, value: str, now: datetime, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    expires_at = now + timedelta(seconds=ttl_seconds)
    _RESPONSE_CACHE[key] = (expires_at, value)
    _RESPONSE_CACHE.move_to_end(key)
    while len(_RESPONSE_CACHE) > MAX_CACHE_ENTRIES:
        _RESPONSE_CACHE.popitem(last=False)


def get_daily_calls(db: Session, day: date, user_id: int | None) -> int:
    """Return the recorded AI call count for a day (user-specific or global when user_id=None)."""
    if user_id is None:
        stmt = select(AiUsageDaily.calls).where(
            AiUsageDaily.day == day, AiUsageDaily.user_id.is_(None)
        )
    else:
        stmt = select(AiUsageDaily.calls).where(
            AiUsageDaily.day == day, AiUsageDaily.user_id == user_id
        )
    return db.scalar(stmt) or 0


def get_remaining_quota(db: Session, user_id: int, cfg: Settings | None = None) -> int:
    """Return remaining AI calls available to the user today."""
    active_cfg = cfg or settings
    today = get_now().date()
    user_calls = get_daily_calls(db, today, user_id)
    global_calls = get_daily_calls(db, today, None)
    user_rem = max(0, active_cfg.AI_DAILY_LIMIT_PER_USER - user_calls)
    global_rem = max(0, active_cfg.AI_DAILY_LIMIT_GLOBAL - global_calls)
    return min(user_rem, global_rem)


def _increment_usage(db: Session, day: date, user_id: int) -> None:
    """Atomically increment per-user and global daily call counters."""
    user_stmt = (
        pg_insert(AiUsageDaily)
        .values(day=day, user_id=user_id, calls=1)
        .on_conflict_do_update(
            index_elements=["day", "user_id"],
            index_where=AiUsageDaily.user_id.is_not(None),
            set_={"calls": AiUsageDaily.calls + 1},
        )
    )
    global_stmt = (
        pg_insert(AiUsageDaily)
        .values(day=day, user_id=None, calls=1)
        .on_conflict_do_update(
            index_elements=["day"],
            index_where=AiUsageDaily.user_id.is_(None),
            set_={"calls": AiUsageDaily.calls + 1},
        )
    )
    db.execute(user_stmt)
    db.execute(global_stmt)
    db.commit()


def _log_metadata(feature: str, status: str, started: float) -> None:
    latency_ms = (time.monotonic() - started) * 1000.0
    logger.info("ai_call feature=%s status=%s latency_ms=%.1f", feature, status, latency_ms)


def guard_ai_call(
    db: Session,
    user: User,
    feature: str,
    system: str,
    user_prompt: str,
    max_tokens: int | None = None,
    provider: AIProvider | None = None,
    cfg: Settings | None = None,
) -> str:
    """Execute a guarded AI completion enforcing kill switch, consent, caps, limits, and cache."""
    started = time.monotonic()
    active_cfg = cfg or settings
    if not active_cfg.AI_ENABLED:
        _log_metadata(feature, "disabled", started)
        raise AIDisabledException()
    if user.ai_consent_at is None:
        _log_metadata(feature, "consent_required", started)
        raise ForbiddenException(
            message="AI consent is required before using AI assistance.",
            code="AI_CONSENT_REQUIRED",
        )
    if len(system) > MAX_SYSTEM_PROMPT_CHARS or len(user_prompt) > MAX_USER_PROMPT_CHARS:
        _log_metadata(feature, "input_too_long", started)
        raise AppException(
            message="AI prompt exceeds maximum allowed length.",
            code="AI_INPUT_TOO_LONG",
            status_code=400,
        )

    effective_tokens = min(
        max_tokens or active_cfg.AI_MAX_OUTPUT_TOKENS,
        active_cfg.AI_MAX_OUTPUT_TOKENS,
    )
    now = get_now()
    key = _cache_key(feature, system, user_prompt, effective_tokens)
    cached = _get_cached(key, now)
    if cached is not None:
        _log_metadata(feature, "cache_hit", started)
        return cached

    today = now.date()
    if get_daily_calls(db, today, None) >= active_cfg.AI_DAILY_LIMIT_GLOBAL:
        _log_metadata(feature, "global_rate_limited", started)
        raise RateLimitExceededException(
            message="Global daily AI usage limit reached.",
            code="AI_GLOBAL_LIMIT_EXCEEDED",
        )
    if get_daily_calls(db, today, user.id) >= active_cfg.AI_DAILY_LIMIT_PER_USER:
        _log_metadata(feature, "user_rate_limited", started)
        raise RateLimitExceededException(
            message="Daily AI usage limit reached for your account.",
            code="AI_USER_LIMIT_EXCEEDED",
        )

    active_provider = provider or get_ai_provider(active_cfg)
    try:
        raw_output = active_provider.complete(system, user_prompt, effective_tokens)
    except AIProviderError:
        _log_metadata(feature, "provider_error", started)
        raise

    sanitized = sanitize_ai_output(raw_output)
    _increment_usage(db, today, user.id)
    _put_cached(key, sanitized, now, active_cfg.AI_CACHE_TTL_SECONDS)
    _log_metadata(feature, "success", started)
    return sanitized


def call_ai_with_fallback(
    db: Session,
    user: User,
    feature: str,
    system: str,
    user_prompt: str,
    fallback_fn: Callable[[], str],
    max_tokens: int | None = None,
    provider: AIProvider | None = None,
    cfg: Settings | None = None,
) -> tuple[str, bool]:
    """Run guarded AI call and fall back to rule-based output when AI is off or failing."""
    try:
        text = guard_ai_call(
            db=db,
            user=user,
            feature=feature,
            system=system,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            provider=provider,
            cfg=cfg,
        )
        return text, True
    except (AIDisabledException, AIProviderError):
        return fallback_fn(), False
