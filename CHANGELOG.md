# Changelog

All notable changes to the **University Learning &amp; Internship Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - Unreleased

### Added
- **Phase 8a: Course Learning Resources**:
  - `course_resources` database model and Alembic migration with cascade foreign key and index on `course_id`.
  - Backend endpoints under `/api`: `GET /api/courses/{id}/resources`, `POST /api/courses/{id}/resources`, `PATCH /api/resources/{id}`, and `DELETE /api/resources/{id}` with thin routers and domain logic in `services/course_resource.py`.
  - Access controls: resources are visible to owner instructor, platform admin, or enrolled students on published courses (draft courses or non-enrolled students return 404). Only owner instructors can add, edit, or delete resources.
  - Strict input validation rejecting `javascript:`, `data:`, non-http(s) schemes, null bytes, and control characters, with extra fields forbidden and a 50-resource limit per course.
  - Frontend `CourseResourcesSection` component with list, modal forms, `ConfirmModal` deletion dialogues, and clear empty states for owners vs enrolled students.
  - Realistic demo course resources seeded into demo dataset with idempotency guards and extended seed tests.
  - OpenAPI documentation synchronized in `docs/openapi.json`.
- **Phase 8b: In-App Notifications**:
  - `notifications` database model with `notification_kind` enum, foreign key with cascade to `users.id`, relative `link_path` validation, and indexed `is_read` and `created_at`.
  - Alembic migration `f5b72183c0aa` creating `notifications` table and PostgreSQL database trigger `trg_prune_notifications` calling `prune_user_notifications()` automatically enforcing a 200-item ceiling per recipient user.
  - Domain event triggers across service layer for 10 distinct events: submission graded, application decision, assignment created, first submission on assignment, application received, internship review status, organization review status, new organization registration, internship submitted for review, and administrative password reset.
  - Actor exclusion logic preventing self-notifications on user-initiated actions.
  - Thin router endpoints under `/api`: `GET /api/notifications`, `GET /api/notifications/unread-count`, `PATCH /api/notifications/{id}/read`, and `POST /api/notifications/read-all`.
  - Frontend `NotificationBell` with unread badge counter, `useUnreadCount` hook with 60-second document visibility polling and focus refetch, `NotificationsPage` with unread highlights, filter, individual mark-as-read, and bulk read-all actions.
  - Realistic notification seeding across demo personas with idempotency guards and extended seed tests.
  - OpenAPI schema synchronization and documentation updates across `database.md`, `architecture.md`, `api.md`, `requirements.md`, `user-guide.md`, and `README.md`.
- **Phase 8c: Internship Coordinator Role**:
  - `coordinator` role added to native PostgreSQL `user_role` enum via Alembic migration `4486e293b423` using `autocommit_block()`.
  - Self-registration restricted to student and organization; coordinators can only be provisioned by administrators via the admin user form or `scripts/create_user.py`.
  - Server-side role enforcement: coordinators and admins may list and decide on organization approvals (`/api/admin/organizations*`), review, approve, reject with notes, and take down internship postings (`/api/admin/internships*`), list all platform internships across all statuses, and read applicant rosters in read-only mode (`/api/internships/{id}/applications`).
  - Strict security boundaries: coordinators are forbidden (`403 Forbidden`) from user administration (`/api/admin/users*`), administrative password resets, course administration, or system health status.
  - Dual notifications: events that notify admins (new organization registered, internship submitted for review) notify both active admins and coordinators.
  - Dedicated coordinator dashboard (`GET /api/dashboard/coordinator`) returning pending organization approvals, postings pending moderation, live open postings, applicant pipeline distribution, and coordinator completed reviews count.
  - Frontend coordinator workspace: custom navigation (Dashboard, Organizations, Internship reviews, Internships, Account, notification bell), dedicated `CoordinatorDashboard` component, route guards, admin user form coordinator option, and badge rendering.
  - Realistic demo coordinator Ms. Selamawit Tadesse seeded into demo dataset, with updated seed tests, user guide, demo script, and documentation.
- **Phase 8d: Achievement Badges &amp; Safe CSV Reports**:
  - Student achievement badges computed dynamically on read from live data without persistent table overhead (`GET /api/students/me/badges`), evaluating 8 milestone definitions (First submission, On-time habit, High achiever, Perfect score, Course finisher, Profile complete, First application, Offer accepted) with progress counters.
  - Centralized safe CSV exporter (`services/csv_export_writer.py`) implementing formula-injection protection (neutralizing cells starting with `=`, `+`, `-`, `@`, `\t`, or `\r` via leading single quote `'`), UTF-8 Byte Order Mark (`\xef\xbb\xbf`) for correct Amharic decoding in Excel, 10,000 row capping, and `Cache-Control: no-store` header.
  - CSV endpoints under `/api`: `GET /api/courses/{id}/gradebook.csv` (owner instructor or admin), `GET /api/internships/{id}/applicants.csv` (owner organization, coordinator, or admin), `GET /api/admin/reports/applications.csv` (coordinator or admin), and `GET /api/admin/reports/users.csv` (admin only, excluding sensitive credentials and hashes).
  - Frontend badges display: Achievements &amp; Badges component on student dashboard and profile page rendering earned badges in solid petrol and unearned badges with progress text.
  - Frontend CSV exports: One-click Export CSV buttons on course detail page, internship applicants section, and dedicated Reports page (`/admin/reports`) for admin and coordinator roles.
  - Seed demo enhancements: Abel earns 6 achievement badges, Meron earns 3; extended seed tests.
  - Refactored `services/assignment.py` into `assignment.py` and `assignment_query.py` to maintain all files strictly under 250 physical lines.
  - Synchronized OpenAPI specification (`docs/openapi.json`) and updated architectural, database, security, and requirements documentation.

### Fixed
- **Documentation Truth Audit**:
  - Corrected password hashing claims to Python standard library `hashlib.scrypt` with 16-byte random salt.
  - Corrected rate limiter description to in-memory sliding-window rate limiting with injectable clock.
  - Corrected course status claims to `draft` and `published` only (removed fictional `archived` status).
  - Corrected internship posting claims by removing fictional `stipend` field (`duration_weeks` represents tenure).
  - Corrected organization profile claims by removing fictional `company_size` field.
  - Corrected API handler concurrency claims from asynchronous to synchronous threadpool execution.
  - Corrected student application prerequisite claims to require only `university` and `department`.
  - Updated React Router version claim to React Router 7.
  - Replaced hard-coded test counts with exact execution commands (`pytest` and `npm run test`).
  - Updated `README.md` architecture diagram to show both the Docker path (Nginx on 8080) and local dev path (Vite on 5173).
  - Updated `scripts/create_user.py` help description to `scrypt`, removed CLI `--password` argument, and added environment variable support (`CREATE_USER_PASSWORD` or `PASSWORD`) with secure fallback to `getpass`.
  - Removed obsolete one-off `scripts/docker_check.py` test script.

---

## [1.0.0] - 2026-10-23

### Added
- **Phase 0: Foundation & Architecture**:
  - FastAPI application structure, database connection pooling via `psycopg` 3 and SQLAlchemy 2, and Alembic version-controlled migration harness.
  - React 18 single-page application with TypeScript (strict, zero `any`), Vite reverse-proxy configuration, and Tailwind CSS design tokens (`petrol`, `chalk`, `ink`, `pencil`, `line`, `moss`, `brick`, `marigold`).
  - Base layout shell with responsive mobile drawer navigation and system health probes (`/api/health`, `/api/health/db`).
- **Phase 1: Authentication & Profile Provisioning**:
  - Stateful server-side session management with cryptographically random tokens stored hashed in PostgreSQL and transmitted via `HttpOnly`, `SameSite=Lax` cookies.
  - Scrypt password hashing with per-user cryptographic salts and timing attack defense (`hashlib.scrypt`).
  - Public registration and authentication flows for students and organizations.
  - Student profile management with bio and skill tag lists; organization corporate profiles with industry and website metadata.
  - CLI administrative user creation tool (`scripts/create_user.py`).
- **Phase 2: Academic Course Management & Enrollment**:
  - Course authoring and lifecycle management (`draft`, `published`) for instructors.
  - Searchable public course catalog with keyword, course code, and department filtering.
  - Course enrollment workflows with database-level duplicate guards and withdrawal support (`leave course`).
  - Instructor student roster table displaying enrolled student names, emails, and enrollment dates.
- **Phase 3: Course Assignments & Submission Grading**:
  - Assignment creation with due dates, description prompts, and maximum score values.
  - Student text submission engine with automatic late submission tagging (`is_late=true`) based on UTC server timestamps.
  - Instructor grading interface with numeric score bounding (0 to max points), qualitative feedback comments, and submission locking once graded.
- **Phase 4: Internship Opportunities & Application Pipeline**:
  - Organization internship posting creation with work modes (`remote`, `hybrid`, `onsite`), durations, and deadlines.
  - Student profile prerequisite guard: students with incomplete profiles are blocked from applying to internships until university and department are saved.
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
