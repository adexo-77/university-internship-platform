"""AI provider interface, OpenAI-compatible HTTP client, and deterministic mock."""

from __future__ import annotations

import hashlib
from typing import Protocol

import httpx

from app.core.config import Settings, settings


class AIProviderError(Exception):
    """Base error raised by an AI provider."""


class AIConfigurationError(AIProviderError):
    """Raised when an AI provider lacks required configuration."""


class AITimeoutError(AIProviderError):
    """Raised when an AI provider request exceeds its timeout."""


class AIUpstreamError(AIProviderError):
    """Raised when an AI provider returns an HTTP error or invalid payload."""


class AIProvider(Protocol):
    """Minimal text-completion interface for AI providers."""

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Generate a plain-text completion for the given system and user prompts."""
        ...


class MockProvider:
    """Deterministic in-process AI provider used for offline development and tests."""

    def __init__(self, response_text: str | None = None) -> None:
        self._response_text = response_text

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Return deterministic plain text without performing network I/O."""
        if self._response_text is not None:
            return self._response_text[: max(1, max_tokens * 4)]
        digest = hashlib.sha256(f"{system}\n{user}".encode()).hexdigest()[:8]
        draft = f"Mock AI draft [{digest}] (max_tokens={max_tokens})."
        return draft[: max(1, max_tokens * 4)]


class OpenAICompatibleProvider:
    """HTTP client for OpenAI-compatible chat completions endpoints."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        clean_url = base_url.strip().rstrip("/")
        if not clean_url:
            raise AIConfigurationError("AI_BASE_URL must not be empty.")
        if not api_key.strip():
            raise AIConfigurationError("AI_API_KEY must not be empty.")
        if not model.strip():
            raise AIConfigurationError("AI_MODEL must not be empty.")
        self._endpoint = (
            clean_url
            if clean_url.endswith("/chat/completions")
            else f"{clean_url}/chat/completions"
        )
        self._api_key = api_key.strip()
        self._model = model.strip()
        self._timeout = float(timeout_seconds)
        self._transport = transport

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        """Call chat completions with a single retry on timeout or 5xx responses."""
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(2):
            try:
                with httpx.Client(timeout=self._timeout, transport=self._transport) as client:
                    response = client.post(self._endpoint, json=payload, headers=headers)
            except httpx.TimeoutException as exc:
                if attempt == 0:
                    continue
                raise AITimeoutError("AI provider request timed out.") from exc
            except httpx.HTTPError as exc:
                raise AIUpstreamError("AI provider connection failed.") from exc

            if response.status_code >= 500:
                if attempt == 0:
                    continue
                raise AIUpstreamError(
                    f"AI provider returned server error ({response.status_code})."
                )
            if response.status_code >= 400:
                raise AIUpstreamError(f"AI provider rejected request ({response.status_code}).")

            return self._extract_content(response)

        raise AIUpstreamError("AI provider failed after retry.")

    @staticmethod
    def _extract_content(response: httpx.Response) -> str:
        try:
            data = response.json()
            choices = data["choices"]
            content = choices[0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIUpstreamError("AI provider returned malformed response payload.") from exc
        if not isinstance(content, str):
            raise AIUpstreamError("AI provider response content must be text.")
        return content


def get_ai_provider(cfg: Settings | None = None) -> AIProvider:
    """Build the configured AI provider without leaking credentials."""
    active_cfg = cfg or settings
    if active_cfg.AI_PROVIDER == "mock":
        return MockProvider()
    base_url = active_cfg.AI_BASE_URL or ""
    api_key = active_cfg.AI_API_KEY.get_secret_value() if active_cfg.AI_API_KEY else ""
    model = active_cfg.AI_MODEL or ""
    if not base_url.strip() or not api_key.strip() or not model.strip():
        raise AIConfigurationError(
            "OpenAI-compatible provider requires AI_BASE_URL, AI_API_KEY, and AI_MODEL."
        )
    return OpenAICompatibleProvider(
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=active_cfg.AI_TIMEOUT_SECONDS,
    )
