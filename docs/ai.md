# AI Foundation Architecture &bull; Privacy, Safety &amp; Operations

This document describes the **AI Foundation (Phase A)** infrastructure for the
**University Learning &amp; Internship Platform**. Phase A introduces the underlying
infrastructure only. There are no user-visible generative AI features in this phase.

---

## 1. Design Philosophy

- **Off by default**: AI is disabled unless `AI_ENABLED=true` is explicitly configured.
- **No external calls in tests or CI**: Tests use the deterministic `MockProvider` and never
  reach a network or a real provider.
- **Zero PII in prompts**: Prompts never include student names, emails, or submission text.
  User-supplied text is treated as data, never as instructions.
- **Plain-text output only**: Control characters are stripped and length is capped before any
  output is returned.
- **Graceful fallback**: When AI is off, slow, or failing, the platform falls back to existing
  rule-based behavior.

---

## 2. Component Layout

| Layer | File | Responsibility |
| :--- | :--- | :--- |
| Configuration | `backend/app/core/config.py` | `AI_ENABLED`, `AI_PROVIDER`, `AI_BASE_URL`, `AI_API_KEY` (`SecretStr`), `AI_MODEL`, `AI_TIMEOUT_SECONDS`, `AI_MAX_OUTPUT_TOKENS`, `AI_DAILY_LIMIT_PER_USER`, `AI_DAILY_LIMIT_GLOBAL`, `AI_CACHE_TTL_SECONDS`. |
| Provider | `backend/app/services/ai_provider.py` | `AIProvider` protocol, `MockProvider`, and `OpenAICompatibleProvider` with retry on timeout and 5xx responses. |
| Guard | `backend/app/services/ai_guard.py` | Kill switch, consent check, prompt length caps, in-memory LRU cache, per-user and global daily quotas, and output sanitizer. |
| Service | `backend/app/services/ai.py` | Status and consent business logic for the signed-in user. |
| Router | `backend/app/routers/ai.py` | `GET /api/ai/status` and `PUT /api/ai/consent` for authenticated users. |
| Model | `backend/app/models/ai_usage_daily.py` | Per-user, per-day call counter backing quota enforcement. |
| Frontend | `frontend/src/components/account/AiSettingsSection.tsx` | Opt-in consent panel on the Account page with a plain-language privacy explanation. |

---

## 3. Data Privacy Model

- **What leaves the system**: only the feature name and a hashed token count are sent to the
  provider when AI is enabled and the user has consented.
- **What never leaves the system**: student names, email addresses, and submission text.
- **Consent**: stored as `users.ai_consent_at`. Users grant or withdraw consent from the Account
  page. All AI endpoints require an authenticated session; identity is resolved from the server
  session cookie, never from the request body.
- **Global kill switch**: when `AI_ENABLED=false`, the guard raises a disabled error and the
  Account page shows that AI assistance is disabled by the platform administrator.

---

## 4. Quotas, Cache &amp; Rate Limiting

- **Per-user daily quota**: `AI_DAILY_LIMIT_PER_USER` (default 10).
- **Global daily quota**: `AI_DAILY_LIMIT_GLOBAL` (default 200).
- **Counters**: persisted in `ai_usage_daily` and keyed by UTC day and user.
- **Retry hint**: when a quota is exceeded the guard raises `RateLimitExceededException` with a
  `Retry-After` value computed as the seconds until the next midnight reset.
- **Cache**: a bounded in-memory LRU cache keyed by feature, prompt, and token budget, with a
  configurable TTL (`AI_CACHE_TTL_SECONDS`).

---

## 5. Provider Abstraction

The `AIProvider` protocol exposes a single `complete(system, user_prompt, max_tokens)` method.

- **MockProvider**: deterministic offline provider used by tests and local development. It never
  performs network I/O.
- **OpenAICompatibleProvider**: targets any OpenAI-compatible endpoint via `AI_BASE_URL`. It
  retries on timeout and 5xx responses, caps output tokens, and never logs the API key.

---

## 6. Local &amp; Offline Development

Set `AI_PROVIDER=mock` (the default) to run fully offline. No API key is required and no network
access is attempted. The frontend consent panel still renders so the opt-in flow can be exercised
end to end without a configured provider.

---

## 7. Verification

- Guard, quota, cache, and sanitizer behavior: `backend/tests/test_ai.py`.
- Provider retry and network isolation: `backend/tests/test_ai_provider.py`.
- Status and consent endpoints: `backend/tests/test_ai_endpoints.py`.
- Frontend hook and panel: `frontend/src/hooks/useAiStatus.test.ts`,
  `frontend/src/components/account/AiSettingsSection.test.tsx`.