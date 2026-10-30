# Requirements Coverage &bull; University Learning &amp; Internship Platform

This document provides traceability between platform capabilities and implementation evidence across the codebase. Each requirement is categorized as **Implemented**, **Partial**, or **Not implemented**, with the corresponding automated tests and UI pages that verify it.

---

## Requirements coverage

| Capability / Requirement | Status | Details | Verification (Test or Page) |
| :--- | :---: | :--- | :--- |
| **Users &amp; RBAC** | **Implemented** | Five distinct roles (`student`, `instructor`, `organization`, `coordinator`, `admin`) with server-side authorization enforcement. | `test_auth_role_sweep.py`, `test_admin_user.py`, `/admin/users` |
| **Student Profiles &amp; Progress** | **Implemented** | Profile fields for university, department, year, bio, skills, work mode, and location preferences with complete-profile application guards. | `test_student_profile.py`, `test_student_profile_preferences.py`, `/profile` |
| **Course Management &amp; Syllabi** | **Implemented** | Course creation with code, department, description, and structured syllabus outline; draft and published lifecycle states. | `test_course_create.py`, `test_course_update.py`, `/courses` |
| **Course Enrollment** | **Implemented** | Published course catalog search, student self-enrollment with duplicate guards, and course withdrawal. | `test_enrollment.py`, `test_course_visibility.py`, `/courses/:id` |
| **Course Learning Resources** | **Implemented** | Curated external documentation and reference links (up to 50 per course) with validated HTTP/HTTPS URLs. Direct binary file uploads are not supported. | `test_course_resource_access.py`, `test_course_resource_rules.py`, `/courses/:id` |
| **Assignment Authoring** | **Implemented** | Instructors create and manage assignments tied to courses with descriptions, maximum point values, and future due dates. | `test_assignment_create.py`, `test_assignment_lifecycle.py`, `/courses/:id` |
| **Assignment Submissions** | **Implemented** | Enrolled students submit text and artifact links; server-side comparison flags late submissions (`is_late=true`); grade locking prevents edits once graded. | `test_submission_lifecycle.py`, `/assignments/:id` |
| **Assignment Grading &amp; Feedback** | **Implemented** | Instructors view student submissions, assign numeric grades strictly bounded between 0 and maximum points, and provide qualitative feedback. | `test_submission_grading.py`, `/assignments/:id/submissions/:subId/grade` |
| **Internship Postings &amp; Catalog** | **Implemented** | Approved organizations author postings with work mode, location, requirements, and deadlines. Filterable catalog displays open postings from approved organizations. | `test_internship_manage.py`, `test_internship_catalog.py`, `test_internship_approval_rules.py`, `/internships` |
| **Internship Moderation Queue** | **Implemented** | Administrators and coordinators review submitted postings, approving or rejecting with actionable review notes, and can take down active listings. | `test_internship_review.py`, `/admin/internships` |
| **Internship Applications** | **Implemented** | Students submit applications with cover letters; withdrawal guards allow cancelling pending applications; organizations manage candidate decisions. | `test_application_apply.py`, `test_application_decision.py`, `/my-applications`, `/internships/:id/applications` |
| **Role-Specific Dashboards** | **Implemented** | Custom dashboard layouts and action metrics for all five personas (student, instructor, organization, coordinator, admin). | `test_dashboard_contract.py`, `/` |
| **Progress Tracking &amp; Metrics** | **Implemented** | Real-time computation of course assignment completion percentages, submission status panels, and due date urgency badges. | `ProgressBar.test.tsx`, `DueBadge.test.tsx`, `SubmissionStatusPanel.test.tsx`, `/` |
| **In-App Notifications** | **Implemented** | Notification center with unread bell counter, All/Unread filter tabs, single mark-as-read, mark all as read, and 200-item capacity pruning trigger. | `test_notification_events.py`, `test_notification_api.py`, `test_seeded_notifications.py`, `/notifications` |
| **Reports &amp; Data Summaries** | **Implemented** | Exportable CSV spreadsheets with formula-injection neutralization for course gradebooks, applicant rosters, applications audit, and user accounts. | `test_csv_gradebook.py`, `test_csv_reports.py`, `/admin/reports` |
| **Milestone Badges** | **Implemented** | Eight dynamically computed student achievement badges based on submissions, on-time submissions, grades, and profile completeness. | `test_badge_boundaries.py`, `test_badge_isolation.py`, `/profile`, `/` |
| **Opportunity Matching** | **Partial** | Deterministic heuristic scoring based on student profile skills (up to 60 pts), work mode (up to 20 pts), and location (up to 20 pts). Machine learning models are not implemented. | `test_internship_suggestions.py`, `test_internship_suggestion_scoring.py`, `/internships` |
| **Rankings &amp; Leaderboards** | **Not implemented** | Out of scope; student evaluation is criterion-based rather than comparative. No competitive ranking algorithms or public scoreboards are built. | Documented architecture decision |
| **Binary File Uploads** | **Not implemented** | Out of scope; resources and submissions use validated external URLs rather than direct binary file storage on the server. | Documented architecture decision |
| **Emailed Password Reset** | **Not implemented** | Out of scope; accounts activate immediately upon registration without third-party email verification. Password resets are handled administratively. | `test_admin_user_lifecycle.py`, `/admin/users` |
| **Cloud Deployment** | **Not implemented** | Out of scope; containerized deployment is configured for local execution via Docker Compose. Cloud deployment topology is documented in architecture specifications. | `docker-compose.yml`, `docs/architecture.md` |

---

## Non-Functional Requirements Verification

| Requirement Area | Specification | Verification Method &amp; Evidence | Status |
| :--- | :--- | :--- | :---: |
| **Security &amp; Sessions** | Stateful server-side sessions, SHA-256 token hashing in DB, `HttpOnly`/`SameSite=Lax` cookies, scrypt password hashing, rate limiting, and 256 KB payload caps. | `test_auth_session.py`, `test_rate_limit.py`, `test_security_headers.py`, `docs/security.md` | **Verified** |
| **Authorization &amp; Multi-Tenancy** | Route-level role dependencies (`require_roles`) and ownership validation in services across courses, assignments, postings, and applications. | `test_authorization_sweep.py`, `test_coordinator_permissions.py` | **Verified** |
| **Data Integrity &amp; Migrations** | Normalized PostgreSQL schema with foreign keys, unique constraints, and linear single-head Alembic migrations. | Alembic migration revisions (`6d7757d439a5` through `4486e293b423`), CI migration checks | **Verified** |
| **Accessibility &amp; Tokens** | Semantic design system palette, WCAG AA contrast ratio compliance (&gt;= 4.5:1), visible focus rings, and explicit form labels. | `palette-guard.test.ts`, `docs/design.md` | **Verified** |
| **Code Modularity** | Thin routers, service layer business logic, strict typing in Python and TypeScript, and strict physical line limit (&lt;= 250 lines per file). | `ruff check`, `eslint`, line count verification | **Verified** |
