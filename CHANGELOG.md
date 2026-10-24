# Changelog

All notable changes to the **University Learning &amp; Internship Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-23

### Added
- **Phase 0: Foundation &amp; Architecture**:
  - FastAPI application structure, database connection pooling via `psycopg` 3 and SQLAlchemy 2, and Alembic version-controlled migration harness.
  - React 18 single-page application with TypeScript (strict, zero `any`), Vite reverse-proxy configuration, and Tailwind CSS design tokens (`petrol`, `chalk`, `ink`, `pencil`, `line`, `moss`, `brick`, `marigold`).
  - Base layout shell with responsive mobile drawer navigation and system health probes (`/api/health`, `/api/health/db`).
- **Phase 1: Authentication &amp; Profile Provisioning**:
  - Stateful server-side session management with cryptographically random tokens stored hashed in PostgreSQL and transmitted via `HttpOnly`, `SameSite=Lax` cookies.
  - Scrypt password hashing with per-user cryptographic salts and timing attack defense (`hashlib.scrypt`).
  - Public registration and authentication flows for students and organizations.
  - Student profile management with bio and skill tag lists; organization corporate profiles with industry, size, and website metadata.
  - CLI administrative user creation tool (`scripts/create_user.py`).
- **Phase 2: Academic Course Management &amp; Enrollment**:
  - Course authoring and lifecycle management (`draft`, `published`, `archived`) for instructors.
  - Searchable public course catalog with keyword, course code, and department filtering.
  - Course enrollment workflows with database-level duplicate guards and withdrawal support (`leave course`).
  - Instructor student roster table displaying enrolled student names, emails, and enrollment dates.
- **Phase 3: Course Assignments &amp; Submission Grading**:
  - Assignment creation with due dates, description prompts, and maximum score values.
  - Student text submission engine with automatic late submission tagging (`is_late=true`) based on UTC server timestamps.
  - Instructor grading interface with numeric score bounding (0 to max points), qualitative feedback comments, and submission locking once graded.
- **Phase 4: Internship Opportunities &amp; Application Pipeline**:
  - Organization internship posting creation with work modes (`remote`, `hybrid`, `onsite`), stipends, and deadlines.
  - Student profile prerequisite guard: students with incomplete profiles are blocked from applying to internships until bio and skills are saved.
  - Student application pipeline with personalized cover letters, application tracking (`/my-applications`), and safe application withdrawal with confirmation dialogs.
  - Employer decision workflows (`shortlisted`, `accepted`, `rejected`) with terminal candidate locking.
- **Phase 5: Institutional Administration &amp; Governance**:
  - Administrative user management: search, filter by role, account activation/deactivation with self-deactivation protection, and administrative password resets.
  - Organization vetting queue: administrative approval required before corporate partners can publish internship listings.
  - Internship content moderation queue: review of submitted postings with approval, rejection with mandatory feedback notes, and administrative listing takedowns.
- **Phase 6: Dashboards, Progress Tracking &amp; Hardening**:
  - Tailored dashboard views for Student, Instructor, Organization, and Administrator personas.
  - Real-time student progress tracking: urgent (due <72h), upcoming, and overdue assignment badges, and recent grade score cards.
  - In-memory rate limiting returning HTTP 429 on authentication routes with frontend cooldown countdown banner and disabled submit actions.
  - Security hardening: CSRF verification, request size limits, and security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`).
- **Phase 7a: Developer Automation, Demo Data &amp; CI**:
  - Cross-platform developer setup script `scripts/setup_dev.py` with version checks, database creation, hidden password input, and migration execution.
  - Idempotent demo dataset seeder `scripts/seed_demo.py` provisioning 6 representative accounts across all roles.
  - GitHub Actions CI workflow (`.github/workflows/ci.yml`) validating backend, frontend, and database migrations on push and pull requests.
- **Phase 7b &amp; 7c: Documentation, OpenAPI &amp; Release Audit**:
  - Exported OpenAPI 3.1 schema specification (`docs/openapi.json`) via `scripts/export_openapi.py`.
  - Backend automated test `test_openapi_export.py` ensuring `docs/openapi.json` stays synchronized with the FastAPI application contract.
  - Full documentation suite: updated `README.md`, `docs/requirements.md` (traceability matrix), `docs/user-guide.md` (role-based walkthrough), `docs/demo-script.md` (8-10 minute presentation and 15 Q&amp;A responses), `docs/api.md`, `docs/architecture.md`, `docs/database.md`, `docs/design.md`, and `docs/security.md`.
  - Dependency and accessibility audit: pruned unused `@testing-library/user-event` package, removed dead type exports, validated WCAG AA color contrast (all active text/background pairs &gt;= 4.5:1), and verified explicit form labels and accessible names on all interactive elements.
- **Phase 7e: Containerization, Orchestration & Release Verification**:
  - Multi-stage `backend/Dockerfile` using pinned `python:3.12.7-slim-bookworm` with non-root security context (`appuser:appgroup`, uid 10001), runtime dependency separation, and curl health check.
  - Multi-stage `frontend/Dockerfile` utilizing `node:20.18.0-alpine` build stage and `nginx:1.27.2-alpine` runtime with SPA fallback, gzip compression, security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`), and `/api` reverse proxy pass.
  - Container orchestration via `docker-compose.yml` linking `db` (PostgreSQL 16.4 with healthcheck and named volume), `backend` (automatic Alembic migration and uvicorn on port 8000), and `frontend` (exposed on host port 8080).
  - One-command demo database seeding via `docker compose run --rm backend python scripts/seed_demo.py`.
  - CI automation job `docker-smoke` in GitHub Actions validating container builds, Compose startup with `--wait`, health endpoints, and clean teardown.
  - Comprehensive documentation accuracy review: added Docker Quick Start, public demo account password matrix, container architecture topology, and corrected test counts.
- **Docker Startup Ordering, Dynamic Upstream & Security Header Deduplication**:
  - Enforced strict startup ordering in `docker-compose.yml` with backend `service_healthy` condition on the frontend and 20s migration `start_period`.
  - Configured Nginx dynamic upstream resolution via Docker embedded DNS (`127.0.0.11`) and retry directives (`proxy_next_upstream`) to gracefully handle backend restarts.
  - Eliminated duplicate HTTP defensive headers on `/api` routes by letting backend headers pass through single-sourced, scoping Nginx headers exclusively to static assets, and removing deprecated `X-XSS-Protection`.
  - Explicitly negated `.env.example` and `.env.docker.example` in ignore files to guarantee template tracking.

### Changed
- Standardized FastAPI and frontend package versions to `1.0.0`.
- Excluded test-only routes from OpenAPI schema generation via `include_in_schema=False`.
