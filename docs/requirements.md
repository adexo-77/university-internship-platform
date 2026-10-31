# Requirements Coverage &bull; University Learning &amp; Internship Platform

This document provides traceability between platform capabilities and implementation evidence
across the codebase. Each requirement is categorized as **Implemented**, **Partial**, or
**Not implemented**, with the corresponding automated tests and UI pages that verify it.

---

## Requirements coverage

### Functional Requirements

| Capability / Requirement | Status | Details | Verification (Test or Page) |
| :--- | :---: | :--- | :--- |
| **Users &amp; RBAC** | **Implemented** | Five distinct roles (`student`, `instructor`, `organization`, `coordinator`, `admin`) with server-side authorization enforcement. | `test_authorization_sweep.py`, `test_admin_user.py`, `/admin/users` |
| **Student Profiles &amp; Progress** | **Implemented** | Profile fields for university, department, year, bio, skills, work mode, and location preferences; incomplete profiles block internship applications until filled. | `test_student_profile.py`, `test_student_profile_preferences.py`, `/profile` |
| **Course Management &amp; Syllabi** | **Implemented** | Course creation with code, department, description, and structured syllabus outline; `draft` and `published` lifecycle states. | `test_course_create.py`, `test_course_update.py`, `/courses` |
| **Course Enrollment** | **Implemented** | Published course catalog search, student self-enrollment with duplicate guards, and course withdrawal. | `test_enrollment.py`, `test_course_visibility.py`, `/courses/:id` |
| **Course Learning Resources** | **Implemented** | Curated external documentation and reference links (up to 50 per course) with validated HTTP/HTTPS URLs. Direct binary file uploads are not supported. | `test_course_resource_access.py`, `test_course_resource_rules.py`, `/courses/:id` |
| **Assignment Authoring** | **Implemented** | Instructors create and manage assignments tied to courses with descriptions, maximum point values, and future due dates. | `test_assignment_create.py`, `test_assignment_lifecycle.py`, `/courses/:id` |
| **Assignment Submissions** | **Implemented** | Enrolled students submit text and artifact links; server-side comparison flags late submissions (`is_late=true`); grade locking prevents edits once graded. | `test_submission_lifecycle.py`, `/assignments/:id` |
| **Assignment Grading &amp; Feedback** | **Implemented** | Instructors view student submissions, assign numeric grades strictly bounded between 0 and maximum points, and provide qualitative feedback. | `test_submission_grading.py`, `/assignments/:id/submissions/:subId/grade` |
| **Internship Postings &amp; Catalog** | **Implemented** | Approved organizations author postings with work mode, location, requirements, and deadlines. Filterable catalog shows only open postings from approved organizations. | `test_internship_manage.py`, `test_internship_catalog.py`, `test_internship_approval_rules.py`, `/internships` |
| **Internship Coordinator Role** | **Implemented** | Dedicated liaison role for organization vetting and posting moderation. Coordinators approve/reject organizations, moderate postings with review notes, inspect all listings, and view applicant rosters read-only. Strictly excluded from user administration and courses. | `test_coordinator_permissions.py`, `test_coordinator_lifecycle.py`, `test_authorization_sweep.py`, `/` |
| **Internship Moderation Queue** | **Implemented** | Administrators and coordinators review submitted postings, approving or rejecting with actionable review notes, and can take down active listings. | `test_internship_review.py`, `test_coordinator_permissions.py`, `/admin/internships` |
| **Internship Applications** | **Implemented** | Students submit applications with cover letters; withdrawal guards allow cancelling pending applications; organizations manage candidate decisions (`submitted` &rarr; `shortlisted` &rarr; `accepted`/`rejected`). | `test_application_apply.py`, `test_application_decision.py`, `/my-applications` |
| **Role-Specific Dashboards** | **Implemented** | Custom dashboard layouts and action metrics for all five personas (student, instructor, organization, coordinator, admin). | `test_dashboard_contract.py`, `/` |
| **Progress Tracking &amp; Metrics** | **Implemented** | Real-time computation of course assignment completion percentages, submission status panels, and due date urgency badges. | `test_dashboard_contract.py`, `DueBadge.test.tsx`, `/` |
| **In-App Notifications** | **Implemented** | Notification center with unread bell counter, All/Unread filter tabs, single mark-as-read, mark-all-as-read, and automatic 200-item capacity pruning via PostgreSQL trigger. Push, SMS, and email notifications are out of scope. | `test_notification_events.py`, `test_notification_admin_events.py`, `test_notification_api.py`, `test_notification_rules.py`, `test_seeded_notifications.py`, `/notifications` |
| **Reports &amp; CSV Exports** | **Implemented** | Exportable CSV spreadsheets with formula-injection neutralization for course gradebooks, internship applicant rosters, application audit, and user account registries. | `test_csv_gradebook.py`, `test_csv_reports.py`, `/admin/reports` |
| **Milestone Badges** | **Implemented** | Eight dynamically computed student achievement badges (First Submission, On-Time Habit, High Achiever, Perfect Score, Course Finisher, Profile Complete, First Application, Offer Accepted) with progress indicators. | `test_badge_boundaries.py`, `test_badge_isolation.py`, `/profile`, `/` |
| **Opportunity Matching** | **Partial** | Deterministic heuristic scoring based on profile skills (up to 60 pts), work mode (up to 20 pts), and location (up to 20 pts). Machine learning models are not implemented. | `test_internship_suggestions.py`, `test_internship_suggestion_scoring.py`, `/internships` |
| **Rankings &amp; Leaderboards** | **Not implemented** | Student ranking algorithms and competitive scoreboards are out of scope; evaluation is criterion-based via milestone badges. | Documented architecture decision |
| **Binary File Uploads** | **Not implemented** | Resources and submissions use validated external URLs rather than direct binary file storage. | Documented architecture decision |
| **Emailed Password Reset** | **Not implemented** | Accounts activate immediately upon registration; password resets are handled administratively. | `test_admin_user_lifecycle.py`, `/admin/users` |
| **Cloud Deployment** | **Not implemented** | Containerized deployment is configured for local execution via Docker Compose; cloud deployment topology is not provisioned. | `docker-compose.yml`, `docs/architecture.md` |

---

### Non-Functional Requirements Verification

| Requirement Area | Specification | Verification Method &amp; Evidence | Status |
| :--- | :--- | :--- | :---: |
| **Security &amp; Sessions** | Stateful server-side sessions, SHA-256 token hashing in PostgreSQL, `HttpOnly`/`SameSite=Lax` cookies, `hashlib.scrypt` password hashing (per-user salt), sliding-window rate limiting, CSRF origin verification, and 256 KB payload limit. | `test_auth_session.py`, `test_auth_login.py`, `test_auth_password_change.py`, `test_rate_limit.py`, `test_security_headers.py`, `docs/security.md` | **Verified** |
| **Authorization &amp; RBAC** | Server-side role enforcement (`require_roles`) across all five personas; strict multi-tenant isolation; cross-tenant modification prohibited. Pending organizations may create and edit draft postings but cannot submit for review or publish until approved. | `test_authorization_sweep.py`, `test_coordinator_permissions.py`, `test_internship_approval_rules.py` | **Verified** |
| **Data Integrity &amp; Migrations** | Normalized PostgreSQL schema with foreign keys, unique constraints, cascading deletes, and single-head Alembic migration history. | Alembic revisions `6d7757d439a5` through `4486e293b423`; CI migration health check | **Verified** |
| **Usability &amp; Accessibility** | Responsive Tailwind CSS design system with semantic tokens, WCAG AA contrast ratio (&gt;= 4.5:1), visible focus rings, and explicit form labels. | `palette-guard.test.ts`, `docs/design.md` | **Verified** |
| **Maintainability** | Thin routers, service layer business logic, strict Python and TypeScript typing, 250-line file limit, zero linter warnings. | `ruff check`, `eslint`, PowerShell line count verification | **Verified** |
| **Testability &amp; CI** | Full automated test coverage across backend (Pytest) and frontend (Vitest + React Testing Library) validated in CI on every push. | `test_authorization_sweep.py`, `DashboardPage.test.tsx`, `.github/workflows/ci.yml` | **Verified** |
