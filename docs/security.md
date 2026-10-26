# Security Architecture &bull; Threat Model &amp; Controls Matrix

This document details the security posture, threat model, control mechanisms, known limitations, and production operational hardening recommendations for the **University Learning & Internship Platform**.

---

## 1. Threat Model &amp; Attack Surface Analysis

| Threat / Attack Vector | Risk Level | Target Assets | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Credential Stuffing &amp; Brute Force** | High | `/api/auth/login`, `/api/auth/register`, `/api/auth/change-password` | Sliding-window in-memory rate limiting with per-IP and per-(IP+email) buckets. Frontend countdown &amp; button locking. |
| **Cross-Site Request Forgery (CSRF)** | High | State-modifying endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) | Origin and Referer validation middleware blocking requests from unapproved third-party origins. |
| **Clickjacking** | Medium | Web UI and authenticated sessions | `X-Frame-Options: DENY` header prevents framing in hostile sites. |
| **MIME Sniffing** | Medium | API and media responses | `X-Content-Type-Options: nosniff` header blocks content sniffing. |
| **CSV Formula Injection** | High | CSV spreadsheet downloads | Prepends single quote `'` to cells starting with `=`, `+`, `-`, `@`, `\t`, or `\r`. |
| **Credential & Hash Leakage in Exports** | High | User account data exports | Whitelist-only row mapping in `services/csv_export.py`; strict exclusion of password hashes and tokens. |
| **Denial of Service (Large Payloads)** | High | API request handling &amp; memory | Request size limiting middleware blocking requests exceeding 256 KB (`HTTP 413 Payload Too Large`). |
| **Denial of Service (Unbounded CSV Export)** | Medium | CSV export queries &amp; buffers | Strict 10,000 row cap on all CSV exports (`MAX_CSV_ROWS`). |
| **PostgreSQL Driver Crashes (NUL Bytes)** | High | Database driver (`psycopg`) and auth queries | Pydantic string sanitization rejecting NUL bytes (`\x00`) and control characters with `422 Unprocessable Entity`. |
| **Session Hijacking &amp; Token Exposure** | High | User credentials &amp; session states | `HttpOnly`, `SameSite=Lax`, `Secure` (production) cookies. Database stores SHA-256 token hashes, never raw tokens. |
| **Sensitive Data Exposure in Errors/Logs** | Medium | Stack traces, password hashes, secrets | Structured logging filtering passwords and tokens; generic JSON 500 handler returning only UUID `request_id`. |

---

## 2. Security Controls Matrix

| Control Category | Implementation File | Key Configurations &amp; Enforcement Rules |
| :--- | :--- | :--- |
| **CSV Injection Defense** | `backend/app/services/csv_export_writer.py` | Prepends `'` to dangerous formula trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`); prepends UTF-8 BOM (`\xef\xbb\xbf`) for safe Amharic rendering; caps output at 10,000 rows; sets `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`. |
| **Data Exposure Guard** | `backend/app/services/csv_export.py` | Strict field projection: `users.csv` exports only `id`, `name`, `email`, `role`, `active`, and `created_at`. Password hashes, reset tokens, and session identifiers are never queried or emitted. |
| **Rate Limiter** | `backend/app/core/rate_limit.py` | Sliding window: 5 failed logins / 15 min per (IP+email), 20 / 15 min per IP, 10 registrations / hr per IP, 5 password changes / 15 min per user. Returns `429` with `Retry-After`. |
| **Rate Limit Frontend** | `frontend/src/hooks/useRateLimitCooldown.ts` | Listens for `429` responses with `Retry-After` header, displays live countdown notice, disables submit button. |
| **CSRF Defense** | `backend/app/core/csrf.py` | Validates `Origin` and `Referer` against `CORS_ORIGINS` for mutations. Allows non-browser clients (missing headers). |
| **Security Headers** | `backend/app/core/security_headers.py` | Sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and `Cache-Control: no-store` on auth/dashboards. |
| **Cookie &amp; Session Hygiene** | `backend/app/core/config.py` | In production (`ENVIRONMENT=production`), enforces `COOKIE_SECURE=True` and rejects localhost in `CORS_ORIGINS`. Purges expired sessions at startup &amp; login. |
| **Request Size Limits** | `backend/app/core/request_size.py` | Rejects request payloads greater than 256 KB with `HTTP 413`. |
| **Input Sanitization** | `backend/app/core/sanitization.py` | Strips control characters, rejects `\x00` bytes, and normalizes email addresses via safe NFKC unicode conversion. |
| **Logging &amp; Error Masking** | `backend/app/core/logging.py` | Request logger masking auth payloads; 500 handler logging stack traces server-side and returning clean `{detail, code, request_id}`. |
| **Role Authorization** | `backend/app/core/deps.py` | Mandatory server-side session resolution; explicit per-route role sets enforced via `require_roles(*roles)` returning `HTTP 403` for unauthorized personas. |

---

## 3. Role-Based Access Control (RBAC) &amp; Personas

The platform defines five distinct personas governed by server-enforced role dependencies:

1. **Student (`student`)**:
   - **Capabilities**: Browse published courses, enroll, access course learning resources, submit coursework before deadline, withdraw pending applications, apply to open postings with completed profile, manage academic profile.
   - **Restrictions**: Cannot author courses, grade coursework, moderate postings, approve organizations, or manage users (`403 Forbidden`).
2. **Instructor (`instructor`)**:
   - **Capabilities**: Author and publish courses, curate course learning resources, author assignments, inspect submission rosters, award numeric grades with feedback.
   - **Restrictions**: Cannot apply to postings, moderate postings, approve organizations, manage users, or grade unowned courses (`403 Forbidden`).
3. **Organization (`organization`)**:
   - **Capabilities**: Author internship postings (`draft`, `pending_review`, `open`, `closed`), extend deadlines up to 90 days, manage candidate pipeline decisions (`shortlisted`, `accepted`, `rejected`), manage corporate profile.
   - **Restrictions**: Unapproved organizations cannot submit postings for review; cannot access academic course rosters or administer users (`403 Forbidden`).
4. **Internship Coordinator (`coordinator`)**:
   - **Capabilities**: Review and decide organization registrations (`/api/admin/organizations*`), moderate internship postings (`/api/admin/internships*`: approve, reject with notes, takedowns), search and view all platform internships across all statuses, inspect candidate applicant rosters (read-only), dedicated coordinator dashboard.
   - **Restrictions**: Strictly forbidden from user account administration (`/api/admin/users*`), administrative password resets, course administration, or system health status (`403 Forbidden`).
5. **Administrator (`admin`)**:
   - **Capabilities**: Superuser role retaining every coordinator privilege plus complete user administration (`/api/admin/users*`), administrative password resets, account activation/deactivation (with self-protection), course administration, and system health status.

---

## 4. Known Limitations &amp; Design Tradeoffs

1. **In-Memory Rate Limiting**:
   - The sliding-window rate limiter stores attempt timestamps in process memory.
   - *Limitation*: Rate counters reset when the server restarts and are not synchronized across multiple worker processes or instances.
   - *Multi-Instance Requirement*: Production clusters with multiple uvicorn workers or container replicas should substitute an external Redis-backed sliding-window limiter.
2. **Email Verification**:
   - Accounts are active immediately upon registration without email confirmation.
3. **Password Recovery**:
   - No self-service email-based password reset exists; password resets are performed by platform administrators via `/api/admin/users/{id}/password`.
4. **Audit Trail Storage**:
   - Structured security events are emitted to standard output (stdout) for ingestion by log collectors; they are not saved to an immutable database audit log.

---

## 5. Production Deployment Recommendations

1. **TLS / HTTPS Termination**:
   - Deploy backend behind a secure reverse proxy (Nginx, Traefik, Caddy, or Cloud Load Balancer) terminating TLS 1.3.
2. **Reverse Proxy Configuration**:
   - Enable `TRUSTED_PROXY=True` in environment variables so `X-Forwarded-For` is securely parsed for client IP tracking.
3. **Content Security Policy (CSP)**:
   - Configure a strict CSP header at the reverse proxy or CDN layer (e.g., `default-src 'self'`).
4. **Database Transport Security**:
   - Set PostgreSQL connection strings with `sslmode=require` or `sslmode=verify-full`.
5. **Secret Rotation**:
   - Regularly rotate `SECRET_KEY` and database credentials in production `.env`.
