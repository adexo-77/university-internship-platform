"""Unit tests for AI guard layer, sanitizer, quota enforcement, cache, and fallback."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ForbiddenException, RateLimitExceededException
from app.models.ai_usage_daily import AiUsageDaily
from app.models.user import User, UserRole
from app.services.ai_guard import (
    AIDisabledException,
    call_ai_with_fallback,
    clear_ai_cache,
    guard_ai_call,
    sanitize_ai_output,
)
from app.services.ai_provider import AITimeoutError, MockProvider
from tests.factories import create_test_user

AI_ON_CFG = Settings(  # type: ignore[call-arg]
    AI_ENABLED=True,
    AI_PROVIDER="mock",
    AI_DAILY_LIMIT_PER_USER=10,
    AI_DAILY_LIMIT_GLOBAL=200,
    AI_CACHE_TTL_SECONDS=3600,
    AI_MAX_OUTPUT_TOKENS=400,
    AI_TIMEOUT_SECONDS=10,
)
AI_OFF_CFG = Settings(  # type: ignore[call-arg]
    AI_ENABLED=False,
    AI_PROVIDER="mock",
    AI_DAILY_LIMIT_PER_USER=10,
    AI_DAILY_LIMIT_GLOBAL=200,
    AI_CACHE_TTL_SECONDS=3600,
    AI_MAX_OUTPUT_TOKENS=400,
    AI_TIMEOUT_SECONDS=10,
)
_FROZEN_DAY = datetime(2026, 11, 10, 12, 0, 0, tzinfo=UTC).date()


def _consented_user(db: Session, email: str) -> User:
    user = create_test_user(db=db, email=email, role=UserRole.STUDENT)
    user.ai_consent_at = datetime(2026, 11, 10, 12, 0, 0, tzinfo=UTC)
    db.commit()
    db.refresh(user)
    return user


def test_sanitize_strips_control_chars_caps_length_and_normalizes_crlf() -> None:
    raw = "hello\x00\x07world\x1b[31m"
    result = sanitize_ai_output(raw)
    assert "\x00" not in result
    assert "\x07" not in result
    assert "\x1b" not in result
    assert "helloworld" in result
    assert len(sanitize_ai_output("A" * 5000, max_chars=100)) <= 100
    assert sanitize_ai_output("line1\r\nline2\rline3") == "line1\nline2\nline3"


def test_guard_raises_when_ai_disabled(real_db_session: Session) -> None:
    user = _consented_user(real_db_session, "ai_disabled@example.com")
    with pytest.raises(AIDisabledException):
        guard_ai_call(
            db=real_db_session,
            user=user,
            feature="test",
            system="sys",
            user_prompt="prompt",
            provider=MockProvider(),
            cfg=AI_OFF_CFG,
        )


def test_guard_raises_403_without_consent(real_db_session: Session) -> None:
    user = create_test_user(
        db=real_db_session, email="ai_noconsent@example.com", role=UserRole.STUDENT
    )
    with pytest.raises(ForbiddenException) as exc_info:
        guard_ai_call(
            db=real_db_session,
            user=user,
            feature="test",
            system="sys",
            user_prompt="prompt",
            provider=MockProvider(),
            cfg=AI_ON_CFG,
        )
    assert exc_info.value.code == "AI_CONSENT_REQUIRED"


def test_guard_allows_10th_call_and_blocks_11th(real_db_session: Session) -> None:
    user = _consented_user(real_db_session, "ai_quota10@example.com")
    stmt = pg_insert(AiUsageDaily).values(day=_FROZEN_DAY, user_id=user.id, calls=9)
    real_db_session.execute(stmt)
    real_db_session.commit()
    clear_ai_cache()

    result = guard_ai_call(
        db=real_db_session,
        user=user,
        feature="test",
        system="sys",
        user_prompt="prompt",
        provider=MockProvider("ok"),
        cfg=AI_ON_CFG,
    )
    assert result == "ok"

    with pytest.raises(RateLimitExceededException) as exc_info:
        guard_ai_call(
            db=real_db_session,
            user=user,
            feature="test",
            system="sys",
            user_prompt="prompt2",
            provider=MockProvider("ok"),
            cfg=AI_ON_CFG,
        )
    assert exc_info.value.code == "AI_USER_LIMIT_EXCEEDED"


def test_guard_blocks_when_global_limit_reached(real_db_session: Session) -> None:
    user = _consented_user(real_db_session, "ai_global_limit@example.com")
    global_cfg = Settings(  # type: ignore[call-arg]
        AI_ENABLED=True,
        AI_PROVIDER="mock",
        AI_DAILY_LIMIT_PER_USER=10,
        AI_DAILY_LIMIT_GLOBAL=200,
        AI_CACHE_TTL_SECONDS=0,
        AI_MAX_OUTPUT_TOKENS=400,
        AI_TIMEOUT_SECONDS=10,
    )
    stmt = pg_insert(AiUsageDaily).values(day=_FROZEN_DAY, user_id=None, calls=200)
    real_db_session.execute(stmt)
    real_db_session.commit()
    clear_ai_cache()

    with pytest.raises(RateLimitExceededException) as exc_info:
        guard_ai_call(
            db=real_db_session,
            user=user,
            feature="test",
            system="sys",
            user_prompt="prompt",
            provider=MockProvider("x"),
            cfg=global_cfg,
        )
    assert exc_info.value.code == "AI_GLOBAL_LIMIT_EXCEEDED"


def test_guard_cache_hit_avoids_second_provider_call(real_db_session: Session) -> None:
    user = _consented_user(real_db_session, "ai_cache@example.com")
    clear_ai_cache()
    call_count = 0

    class CountingMock:
        def complete(self, _system: str, _user: str, _max_tokens: int) -> str:
            nonlocal call_count
            call_count += 1
            return "cached_response"

    guard_ai_call(
        db=real_db_session,
        user=user,
        feature="cache-test",
        system="sys",
        user_prompt="same_prompt",
        provider=CountingMock(),
        cfg=AI_ON_CFG,
    )
    result2 = guard_ai_call(
        db=real_db_session,
        user=user,
        feature="cache-test",
        system="sys",
        user_prompt="same_prompt",
        provider=CountingMock(),
        cfg=AI_ON_CFG,
    )
    assert result2 == "cached_response"
    assert call_count == 1


def test_call_ai_with_fallback_handles_disabled_and_timeout(real_db_session: Session) -> None:
    user = _consented_user(real_db_session, "ai_fallback@example.com")
    clear_ai_cache()

    text_off, used_ai_off = call_ai_with_fallback(
        db=real_db_session,
        user=user,
        feature="test",
        system="sys",
        user_prompt="prompt_off",
        fallback_fn=lambda: "rule-based-off",
        provider=MockProvider("ai"),
        cfg=AI_OFF_CFG,
    )
    assert (text_off, used_ai_off) == ("rule-based-off", False)

    class TimeoutMock:
        def complete(self, _system: str, _user: str, _max_tokens: int) -> str:
            raise AITimeoutError("timed out")

    text_err, used_ai_err = call_ai_with_fallback(
        db=real_db_session,
        user=user,
        feature="test",
        system="sys",
        user_prompt="prompt_timeout",
        fallback_fn=lambda: "rule-based-timeout",
        provider=TimeoutMock(),
        cfg=AI_ON_CFG,
    )
    assert (text_err, used_ai_err) == ("rule-based-timeout", False)


def test_api_key_absent_from_logs(
    real_db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    user = _consented_user(real_db_session, "ai_keylog@example.com")
    clear_ai_cache()
    fake_key = "sk-supersecret-9999"
    cfg_with_key = Settings(  # type: ignore[call-arg]
        AI_ENABLED=True,
        AI_PROVIDER="mock",
        AI_API_KEY=fake_key,
    )
    assert fake_key not in repr(cfg_with_key)
    assert fake_key not in str(cfg_with_key.AI_API_KEY)

    with caplog.at_level(logging.DEBUG, logger="app.ai"):
        guard_ai_call(
            db=real_db_session,
            user=user,
            feature="test",
            system="sys",
            user_prompt="no key here",
            provider=MockProvider("safe output"),
            cfg=cfg_with_key,
        )
    for record in caplog.records:
        assert fake_key not in record.getMessage()
