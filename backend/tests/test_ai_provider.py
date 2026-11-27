"""Unit tests for AI provider layer (MockProvider, OpenAICompatibleProvider, no-network guard)."""

from __future__ import annotations

import httpx
import pytest

from app.core.config import Settings
from app.services.ai_provider import (
    AIConfigurationError,
    AITimeoutError,
    AIUpstreamError,
    MockProvider,
    OpenAICompatibleProvider,
    get_ai_provider,
)


@pytest.fixture(autouse=True)
def _block_real_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail immediately if any code attempts a real HTTP request during tests."""

    def _forbid_network(_self: httpx.HTTPTransport, request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"Real HTTP request forbidden in tests: {request.url}")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", _forbid_network)


def test_mock_provider_returns_deterministic_output() -> None:
    provider = MockProvider()
    out1 = provider.complete("sys", "user", 50)
    out2 = provider.complete("sys", "user", 50)
    assert out1 == out2
    assert "Mock AI draft" in out1


def test_openai_provider_5xx_retries_once_and_succeeds() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        assert request.headers["Authorization"] == "Bearer sk-secret-test-key"
        if attempts == 1:
            return httpx.Response(503, json={"error": "unavailable"})
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Retry succeeded"}}]},
        )

    provider = OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        api_key="sk-secret-test-key",
        model="gpt-test",
        transport=httpx.MockTransport(handler),
    )
    assert provider.complete("sys", "user", 100) == "Retry succeeded"
    assert attempts == 2


def test_openai_provider_timeout_retries_and_raises_without_leaking_key() -> None:
    attempts = 0
    secret = "sk-never-leak-timeout-key"

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("read timed out")

    provider = OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        api_key=secret,
        model="gpt-test",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(AITimeoutError) as exc_info:
        provider.complete("sys", "user", 100)
    assert attempts == 2
    assert secret not in str(exc_info.value)


def test_openai_provider_4xx_fails_without_retry() -> None:
    attempts = 0
    secret = "sk-never-leak-4xx-key"

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(401, json={"error": "unauthorized"})

    provider = OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        api_key=secret,
        model="gpt-test",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(AIUpstreamError) as exc_info:
        provider.complete("sys", "user", 100)
    assert attempts == 1
    assert secret not in str(exc_info.value)


def test_get_ai_provider_requires_credentials_for_openai_compatible() -> None:
    cfg = Settings(  # type: ignore[call-arg]
        AI_ENABLED=True,
        AI_PROVIDER="openai_compatible",
        AI_BASE_URL=None,
        AI_API_KEY=None,
        AI_MODEL=None,
    )
    with pytest.raises(AIConfigurationError):
        get_ai_provider(cfg)


def test_get_ai_provider_returns_mock_by_default() -> None:
    cfg = Settings(AI_PROVIDER="mock")  # type: ignore[call-arg]
    assert isinstance(get_ai_provider(cfg), MockProvider)


def test_real_http_is_blocked_without_mock_transport() -> None:
    provider = OpenAICompatibleProvider(
        base_url="https://example.invalid/v1",
        api_key="sk-test",
        model="gpt-test",
    )
    with pytest.raises(AssertionError, match="Real HTTP request forbidden"):
        provider.complete("sys", "user", 10)
