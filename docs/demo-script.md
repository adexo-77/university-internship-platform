# Demo Walkthrough Script &amp; Q&amp;A Reference

This document provides an **8 to 10 minute end-to-end presentation script** for live demonstrations, followed by **17 key technical questions and accurate answers** grounded directly in this codebase.

---

## 1. 8 to 10 Minute Demo Walkthrough

### Timeline Overview
- **0:00 - 0:45**: Introduction &amp; High-Level Architecture
- **0:45 - 3:00**: Student Persona (Dashboard, Course Enrollment, Late Submission, Internship Application)
- **3:00 - 5:15**: Instructor Persona (Course Creation, Assignment Authoring, Bounded Grading)
- **5:15 - 7:00**: Organization Persona (Company Profile, Posting Lifecycle, Candidate Decisions)
- **7:00 - 8:45**: Administrator Persona (User Management, Org Approvals, Internship Moderation)
- **8:45 - 10:00**: Architectural Summary &amp; Quality Engineering Standards

---

### Step-by-Step Script

#### [0:00 - 0:45] Introduction &amp; Motivation
> **What to Say**:
> *"Welcome! Today I am presenting the University Learning &amp; Internship Platform. Traditional university portals separate academic coursework from career recruitment, creating data silos. This platform integrates course tracking, assignment submissions with strict deadline enforcement, verified corporate internship postings, and university administrative governance into a single, cohesive system.*
>
> *Under the hood, it's powered by FastAPI, PostgreSQL with SQLAlchemy 2, Alembic migrations, and a React 18 TypeScript frontend. Everything has been built with clean modular architecture, zero linter warnings, and over 390 automated tests."*

---

#### [0:45 - 3:00] Part 1: Student Persona
> **Action**: Log in as `abel.tesfaye@example.com` (password `12345678`).

> **What to Say**:
> *"Let's begin from the student perspective. Upon logging in, the student lands on their personalized dashboard. Notice the top stat strip showing enrolled courses, active assignments, and application counts.*
>
> *Look at the 'Assignments Due Soon' panel. Our backend computes urgency in real time: assignments due within 72 hours receive an urgent amber badge, upcoming ones are blue, and overdue items are clearly flagged.*
>
> *Next, let's look at coursework. Under the 'Courses' catalog, students can search courses by code or title and enroll with a single click. When submitting assignments, our backend compares the server timestamp against the due date: if submitted after the deadline, it's accepted but automatically flagged as `is_late=true`.*
>
> *Now, let's observe our profile-complete rule before applying. If we switch to our third student account, `dawit.lemma@example.com`, who has an incomplete profile (missing university and department), a prominent warning banner appears on their dashboard. If they attempt to apply for an internship, the application is blocked until their university and department profile fields are completed. This ensures partner organizations only receive complete applications."*

---

#### [3:00 - 5:15] Part 2: Instructor Persona
> **Action**: Log out and log in as `tadesse.bekele@example.com` (password `12345678`).

> **What to Say**:
> *"Next, let's explore the faculty experience. Instructors have a dedicated dashboard showing active courses, student enrollment totals, and a 'Needs Grading' queue.*
>
> *Instructors can author courses with a course code, department, description, and structured syllabus outline. Courses can be kept in `draft` mode while being prepared and `published` when ready.*
>
> *Under any course, the instructor can create assignments with strict due dates and maximum point values. In the assignment roster, instructors see student submissions in real time.*
>
> *Let's grade a pending submission: clicking 'Grade' opens our grading interface. Notice our validation rules: scores must be numeric between 0 and maximum points—the server rejects out-of-bounds grades with a 422 error. The instructor provides qualitative feedback comments, saves the grade, and the submission status transitions immediately to `graded`, locking it against further student edits."*

---

#### [5:15 - 7:00] Part 3: Organization Persona
> **Action**: Log out and log in as `yohannes.haile@example.com` (Kaffa Digital Solutions, password `12345678`).

> **What to Say**:
> *"Now let's look at corporate recruiting partners. An approved organization manages their corporate profile, including industry category, location, and verified website.*
>
> *Organizations can create internship postings specifying role responsibilities, required skills, work mode—remote, hybrid, or on-site—duration in weeks, and application deadlines. When created, postings enter a `pending_review` state because universities cannot allow unvetted job listings to reach students.*
>
> *Notice our onboarding guard: if we log in as an unverified company, `eyob.kassa@example.com` (Abay Data Labs), they can prepare and edit draft listings, but submitting postings for review or publishing them is blocked until a university administrator or coordinator approves their registration.*
>
> *For approved organizations with active listings, the hiring manager reviews incoming candidate applications, inspects cover letters and student skill tags, and transitions candidates through the pipeline: `shortlisted`, `accepted`, or `rejected`. Once an acceptance or rejection is finalized, the record is locked to maintain hiring integrity."*

---

#### [7:00 - 8:15] Part 4: Administrator Persona
> **Action**: Log out and log in as `mulugeta.assefa@example.com` (Dr. Mulugeta Assefa, password `12345678`).

> **What to Say**:
> *"Next, let's look at institutional governance. University administrators have full visibility over platform operations.*
>
> *First, User Management: admins can search and filter accounts across all roles. Admins can provision new users including internship coordinators, deactivate abusive accounts with self-protection guards, and issue secure password resets that revoke active sessions.*
>
> *Second, Organization Vetting &amp; Moderation: admins review pending company registrations and submitted internship postings before they reach students."*

---

#### [8:15 - 9:00] Part 5: Internship Coordinator Persona
> **Action**: Log out and log in as `selamawit.tadesse@example.com` (Ms. Selamawit Tadesse, password `12345678`).

> **What to Say**:
> *"Now let's examine the Internship Coordinator role. Coordinators are institutional liaisons focused strictly on employer relationships and internship moderation, without administrative access to user accounts, password resets, courses, or system health.*
>
> *On the Coordinator Dashboard, Ms. Selamawit monitors pending employer approvals, postings awaiting review, open internships, application statuses, and her personal completed review count.*
>
> *Coordinators review and approve pending organizations like Abay Data Labs, moderate and publish or reject internship postings, browse all platform listings across every lifecycle, and inspect applicant rosters in read-only mode to track placement health."*

---

#### [9:00 - 10:00] Part 6: Quality Engineering &amp; Wrap-up
> **What to Say**:
> *"To conclude, I'd like to highlight our engineering standards. We adhered strictly to the AGENTS.md constitution throughout development:
> 1. Authentication relies on server-side session tokens stored hashed in PostgreSQL with `HttpOnly` and `SameSite=Lax` cookies—never trusting client headers.
> 2. Passwords use standard library `hashlib.scrypt` hashing with per-user cryptographic salts.
> 3. File sizes are strictly capped under 250 physical lines across all Python, TypeScript, and test files.
> 4. We maintain zero linter warnings on Ruff and ESLint.
> 5. Our test suite includes automated Pytest integration tests against a real PostgreSQL database and Vitest unit and component tests across all frontend suites (runnable with `pytest` and `npm run test`).
>
> Thank you, and I am ready for any questions!"*

---

## 2. Q&amp;A Preparation: 17 Key Technical Questions &amp; Answers

### Q1: Why did you choose FastAPI over traditional frameworks like Django or Flask?
**Answer**: FastAPI provides clean synchronous request handling in worker threadpools with SQLAlchemy 2, strict runtime schema validation via Pydantic v2, and automated OpenAPI documentation out of the box. Its lightweight dependency injection system allows us to enforce database sessions, authentication, and role guards cleanly without the monolithic bloat of Django or the lack of built-in typing in Flask.

### Q2: Why did you use PostgreSQL with `psycopg` 3 and SQLAlchemy 2 instead of raw SQL or an async ORM like Tortoise?
**Answer**: SQLAlchemy 2 offers modern type-safe ORM and 2.0 Core querying with explicit session boundaries, pairing seamlessly with Alembic for version-controlled schema migrations. We chose PostgreSQL because our domain models require relational foreign key integrity, unique constraints, and ACID transactions (e.g., student enrollment guards and candidate state transitions). `psycopg` 3 is the modern, fast standard driver for Python and PostgreSQL.

### Q3: How is authentication and session management implemented?
**Answer**: We implement stateful server-side sessions. Upon login, the backend generates a cryptographically random 32-byte token via `secrets.token_urlsafe(32)`. The token's SHA-256 hash is persisted in the `sessions` table alongside user ID and expiry timestamp. The token is sent to the browser in an `HttpOnly`, `SameSite=Lax` cookie. Identity is decoded on the server per request and is **never** accepted from request bodies or custom headers.

### Q4: How are passwords secured?
**Answer**: User passwords are encrypted using Python's standard library `hashlib.scrypt` with a unique 16-byte random salt per user (N=16384, r=8, p=1). Scrypt provides memory-hardness and ASIC resistance without external C/Rust dependencies. Hashes are persisted in the format `scrypt${salt_hex}${hash_hex}` and are never logged or exposed in API response schemas.

### Q5: How do you enforce authorization and Role-Based Access Control (RBAC)?
**Answer**: RBAC is enforced on the server at two levels: route dependencies (`require_roles(...)` in `app/core/deps.py`) and inside domain services (`app/services/*`). If an unauthorized user attempts an action (e.g., a student calling an instructor grading endpoint), the server raises an HTTP 403 Forbidden. UI visibility guards in React are purely ergonomic conveniences.

### Q6: Why are internship postings reviewed by university administrators and coordinators before going live?
**Answer**: In educational platforms, students are vulnerable to predatory recruiters, unpaid labor violations, or fraudulent job offers. Requiring administrator or coordinator review ensures institutional vetting, protects student safety, and verifies that listed roles, responsibilities, and required skills meet academic standards.

### Q7: Why is organization approval separated from internship posting review?
**Answer**: This represents a defense-in-depth model:
1. Stage 1: Organization verification validates corporate legitimacy (official website URL, industry category, location, and description).
2. Stage 2: Listing moderation reviews the specific opportunity terms, ensuring the job description is suitable for university students.

### Q8: How did you implement assignment deadlines and late submission tracking?
**Answer**: When an assignment is created, a timezone-aware UTC `due_at` timestamp is recorded. When a student submits, the backend captures `submitted_at`. If `submitted_at > due_at`, the system sets `is_late=True`. Once an instructor submits a numeric grade, the submission is permanently locked against further updates to preserve academic honesty.

### Q9: What is your automated testing strategy across the stack?
**Answer**: We employ a comprehensive test pyramid:
- **Backend**: Integration and domain tests executed against a real PostgreSQL test database via `pytest`. Tests cover registration, role sweeps, session expiry, deadline enforcement, bounded grading, and concurrent enrollment.
- **Frontend**: Unit and integration tests using React Testing Library and Vitest via `npm run test`, testing component rendering, form validations, route guards, error boundaries, and WCAG color token compliance.

### Q10: How does the application protect against common web vulnerabilities (OWASP Top 10)?
**Answer**:
- **SQL Injection**: Prevented via SQLAlchemy ORM parameterized queries.
- **XSS**: React automatically escapes untrusted content in JSX; HTML input sanitization is enforced.
- **CSRF**: Mitigated via `SameSite=Lax` session cookies and strict JSON content-type requirements.
- **Broken Object Level Authorization (BOLA/IDOR)**: Service methods verify ownership (e.g., verifying `course.instructor_id == current_user.id` or `internship.organization_id == current_user.id`).
- **Brute Force**: In-memory rate limiting throttles authentication endpoints, returning 429 status codes.

### Q11: Why is there a strict 250 physical line limit per file?
**Answer**: Monolithic files quickly turn into unmaintainable "god classes" with tangled responsibilities. A strict 250 physical line limit forces developers to decompose features into focused, single-responsibility modules (e.g., splitting catalog search, status transitions, and deadline checks into separate domain services).

### Q12: How are rate limits handled on both backend and frontend?
**Answer**: The backend uses an in-memory sliding-window limiter on sensitive endpoints (`/api/auth/login`, `/api/auth/register`, `/api/auth/change-password`). When exceeded, it returns HTTP 429 with a `Retry-After` header. The frontend interceptor detects 429 responses, displays an in-app cooldown countdown banner, and disables the submit button until the cooldown period elapses.

### Q13: What happens if an instructor tries to delete a course with active assignments or enrollments?
**Answer**: Our database models and service methods enforce foreign key integrity. If dependent submissions exist, deletion is rejected with a descriptive business error, preventing orphaned student records and grade loss.

### Q14: Why did you choose a Vite Single-Page Application (SPA) instead of Next.js?
**Answer**: For an internal authenticated portal, Server-Side Rendering (SSR) adds architectural complexity and server node overhead without meaningful benefits. A Vite SPA with strict TypeScript provides instant hot-module replacement during development, minimal bundle size, and a clean separation from our independent FastAPI backend.

### Q15: What features would you implement next in future development?
**Answer**:
1. **External Email & Push Notifications**: Integration with external email providers (AWS SES/SendGrid) and web push alerts (in-app notifications are already fully implemented).
2. **Binary Learning Resources**: S3/MinIO presigned URL integration for PDF slides, assignment attachments, and resume uploads (course resource links are already implemented).
3. **Multi-Institution Federation**: Cross-university credit recognition, multi-campus tenancy, and consortium-wide internship sharing (student achievement badges and safe CSV reports are already fully implemented).
4. **AI-Assisted Candidate Matching**: Currently, deterministic rule-based matching, keyword search, and work-mode filters are implemented; future releases could explore vector embeddings or automated resume parsing.

### Q16: How are student achievement badges calculated and rendered?
**Answer**: Student badges are computed dynamically on read (`services/badge.py`) from live relational data (`submissions`, `assignments`, `courses`, `student_profiles`, `applications`) without storing duplicate state or introducing migration overhead. Eight milestones evaluate submissions, on-time submissions, 90%+ grades, 100% perfect scores, course completion, profile completeness, and internship offers. On the frontend, earned badges appear in solid petrol while unearned ones show subtle progress indicators (e.g., "3 of 5").

### Q17: How does the platform defend CSV spreadsheet downloads against injection attacks?
**Answer**: All CSV reports stream through a safe centralized generator (`services/csv_export_writer.py`). It applies CSV formula-injection neutralization by prefixing any cell starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with a single quote `'`. Responses include a UTF-8 Byte Order Mark (`\xef\xbb\xbf`) so Excel renders Amharic text properly, set `Cache-Control: no-store`, enforce a 10,000 row cap, and project strict public field whitelists that permanently omit password hashes, salts, and session tokens.

