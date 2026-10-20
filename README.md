# University Learning &amp; Internship Platform &bull; Phase 5c Internship Posting Review

A production-grade, modular web platform designed for university student learning tracking, skill assessment, and internship placement matching. Built for the Brolf Tech internship technical challenge with a strict **MVP first, one phase at a time** methodology.

> **Phase 5c Status**: Internship posting review, moderation queue, and lifecycle actions fully operational.
> - **Extended Status Lifecycle**: Internship postings progress through `draft`, `pending_review`, `open`, `rejected`, and `closed`. Direct publishing via PATCH is disabled (returns 409 "Submit for review instead").
> - **Organization Review Workflow**: Approved organizations submit postings for review via `POST /api/internships/{id}/submit`. Postings in `pending_review` can be withdrawn back to `draft` via `POST /api/internships/{id}/withdraw`. Rejected postings can be edited and resubmitted. Open postings can be closed via `POST /api/internships/{id}/close`.
> - **Content Lock &amp; Deadline Extension Cap**: Content is editable only in `draft` or `rejected` status. An `open` posting permits only deadline extensions (shortening returns 409 Conflict) or closure. Application deadlines may never exceed `MAX_DEADLINE_DAYS = 90` days after their reference date (approval date `reviewed_at` for open postings, and today for draft or rejected postings). Violations on create, edit, or extension return 409 Conflict with the latest allowed date. `pending_review` and `closed` postings are strictly immutable.
> - **Admin Review Queue &amp; Takedowns**: Administrators review submitted postings at `/admin/internship-reviews` (`GET /api/admin/internships?status=`, ordered oldest first). Review panel displays full posting details and organization profile with Approve and Reject actions (review note required on rejection). Open postings support administrative takedown with a mandatory note and plain confirmation.
> - **Metadata Privacy &amp; Student Isolation**: `reviewed_by`, `reviewed_at`, and `review_note` are derived from the session and visible exclusively to the posting owner and administrators. Taken-down or rejected postings disappear from student catalogue and detail views (404 Not Found) and reject new applications (409 Conflict) while preserving existing student applications.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+ / 3.14+, FastAPI, SQLAlchemy 2, PostgreSQL (via `psycopg` 3), Alembic, Pydantic v2 |
| **Frontend** | React 18, React Router 6/7, Vite (proxy to backend :8001), TypeScript (strict, no `any`), Tailwind CSS, Lucide React |
| **Testing** | Pytest + FastAPI `TestClient` (backend: 112 tests), Vitest + React Testing Library (frontend: 165 tests) |
| **Tooling &amp; Quality** | Ruff (backend lint &amp; format), ESLint 9 + Prettier (frontend lint &amp; format) |
| **Environment** | Windows PowerShell compatible, Unix LF line endings, no hardcoded Windows paths |

---

## Directory Structure

```text
university-internship-platform/
├── .editorconfig              # Editor consistency rules (LF, UTF-8, indentation)
├── .env.example               # Template environment configuration
├── .gitattributes             # Enforce LF line endings (* text=auto eol=lf)
├── .gitignore                 # Excludes .env, .venv, node_modules, dist, __pycache__, etc.
├── AGENTS.md                  # Project constitution & strict architectural guidelines
├── README.md                  # Setup instructions and PowerShell commands
├── docs/
│   ├── architecture.md        # Architecture, topology, and endpoint contracts
│   ├── database.md            # Mermaid ER diagram, status lifecycle diagram, and schema specifications
│   └── design.md              # Design tokens, components, and layout guidelines
├── scripts/
│   └── create_user.py         # CLI administrative user provisioning tool
├── backend/
│   ├── alembic/               # Database migration environment
│   │   ├── versions/          # Migration revision scripts
│   │   │   ├── 6d7757d439a5_create_users_and_sessions_tables.py
│   │   │   ├── c9e18918b114_create_student_and_organization_.py
│   │   │   ├── f0197aea93a8_create_courses_and_enrollments_tables.py
│   │   │   ├── 340caf61d32f_create_assignments_and_submissions_.py
│   │   │   ├── e17d6f716230_create_internship_postings_and_.py
│   │   │   ├── 7a040b1cdfb8_add_approval_fields_to_organization_.py
│   │   │   └── c4d9a28e57f1_add_review_fields_and_statuses_to_.py
│   │   └── env.py             # Migration harness wired to Base metadata
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development and testing dependencies (pytest, ruff, httpx)
│   ├── app/
│   │   ├── core/              # Settings, database engine, security helpers, deps
│   │   ├── models/            # SQLAlchemy models (user, session, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application)
│   │   ├── schemas/           # Pydantic schemas (auth, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application, health, admin_user, admin_organization, admin_internship)
│   │   ├── routers/           # Thin FastAPI HTTP endpoints (/api only: auth, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application, health, admin_user, admin_organization, admin_internship)
│   │   ├── services/          # Pure business logic and domain rules (auth, student_profile, organization_profile, course, course_catalog, enrollment, assignment, submission, internship, internship_catalog, application, health, admin_user, admin_organization, admin_internship)
│   │   └── main.py            # FastAPI entry point & CORS
│   └── tests/
│       ├── conftest.py        # Pytest fixtures and database test harnesses
│       ├── factories.py       # Test data factories and authentication helpers
│       ├── test_admin_organization.py   # Admin organization approval and status filter tests
│       ├── test_admin_user.py           # Admin user search, role filter, and provisioning tests
│       ├── test_admin_user_lifecycle.py # Admin user activation, self-protection, and password reset tests
│       ├── test_application_apply.py    # Application submission, profile prerequisite, and withdrawal tests
│       ├── test_application_decision.py # Organization application review, decision transitions, and locking tests
│       ├── test_assignment_create.py    # Assignment creation and visibility tests
│       ├── test_assignment_lifecycle.py # Assignment grade floor and deletion guard tests
│       ├── test_auth_login.py           # Auth login tests
│       ├── test_auth_password_change.py # Authenticated password change and session invalidation tests
│       ├── test_auth_register.py        # Auth registration tests
│       ├── test_auth_session.py         # Session lifecycle & role guard tests
│       ├── test_course_create.py        # Course creation permissions and field validation tests
│       ├── test_course_update.py        # Course update and status transition tests
│       ├── test_course_visibility.py    # Course visibility, catalog search, and pagination tests
│       ├── test_enrollment.py           # Enrollment, roster inspection, and cascade delete tests
│       ├── test_health.py               # System & DB health test suite
│       ├── test_internship_approval_rules.py # Approval requirements for internship publishing & catalog hiding
│       ├── test_internship_catalog.py   # Internship catalogue search, work mode filters, and visibility tests
│       ├── test_internship_manage.py    # Internship creation, owner editing, and status transition tests
│       ├── test_internship_review.py    # Admin review queue, approve, reject with note, takedown, and privacy tests
│       ├── test_internship_transitions.py # Posting state transitions, submit, withdraw, close, and deadline guards
│       ├── test_organization_profile_access.py # Organization profile access & guards tests
│       ├── test_organization_profile_update.py # Organization profile update & validation tests
│       ├── test_script_create_user.py   # CLI script integration tests
│       ├── test_student_profile.py      # Student profile integration tests
│       ├── test_submission_grading.py   # Submissions roster, grading and regrading tests
│       └── test_submission_lifecycle.py # Student submission, server-clock late flag, and locking tests
└── frontend/
    ├── eslint.config.js       # ESLint 9 flat configuration
    ├── index.html             # HTML entry with typography and SEO metadata
    ├── package.json           # Frontend dependencies and npm scripts
    ├── postcss.config.js      # PostCSS config
    ├── tailwind.config.js     # Tailwind CSS theme setup
    ├── tsconfig.json          # Strict TypeScript configuration
    ├── tsconfig.node.json     # Vite config TypeScript options
    ├── vite.config.ts         # Vite proxy configuration (/api -> :8001) and Vitest
    └── src/
        ├── api/               # API clients (auth, health, profile, course, assignment, internship, application, admin_user, admin_organization, admin_internship)
        ├── components/
        │   ├── account/       # ChangePasswordForm
        │   ├── admin/         # AdminUsersTable, AdminUserForm, AdminUserStatusModal, AdminResetPasswordModal, AdminOrganizationsTable, AdminOrganizationApprovalModal, AdminInternshipReviewsTable, AdminInternshipReviewModal
        │   ├── assignments/   # AssignmentForm, AssignmentTable, CourseAssignmentsSection, DueBadge, GradeForm, SubmissionForm, SubmissionStatusBadge, SubmissionsTable
        │   ├── courses/       # CourseForm, CourseTable, EnrollButton, StudentRosterTable
        │   ├── internships/   # InternshipForm, InternshipTable, InternshipStatusBadge, ApplyForm, ApplicationStatusBadge, ApplicantsTable, DecisionForm, MyApplicationsTable, StudentApplicationPanel, InternshipApplicantsSection, OrganizationApprovalNotice, InternshipActionsBar, InternshipInfoCard
        │   ├── layout/        # AppShell layout component
        │   ├── profile/       # StudentProfileForm, OrganizationProfileForm
        │   ├── routes/        # ProtectedRoute, RoleRoute
        │   └── ui/            # Reusable UI component library (Button, TextField, DataTable, etc.)
        ├── config/            # Centralized navigation configuration
        ├── context/           # React AuthContext and AuthProvider
        ├── hooks/             # Custom hooks (useAuth, useHealth, usePageTitle)
        ├── lib/               # Utility functions (cn, dates, skills)
        ├── pages/             # Pages (Login, Register, Account, Profile, Courses, MyCourses, CourseCreate, CourseEdit, CourseDetail, AssignmentCreate, AssignmentEdit, AssignmentDetail, SubmissionGrade, Internships, InternshipCreate, InternshipEdit, InternshipDetail, MyInternships, MyApplications, ApplicationDetail, AdminUsers, AdminUserCreate, AdminOrganizations, AdminInternshipReviews, SystemStatus, NotFound)
        ├── types/             # Shared TypeScript types (auth, health, profile, course, assignment, internship, application, admin)
        ├── App.tsx            # Application routing entry point
        └── main.tsx           # React DOM root
```

---

## Prerequisites

Before starting, ensure the following are installed and added to your `PATH`:
- **Python**: 3.12+ or 3.14+ (`python --version`)
- **Node.js**: 20+ or 24+ and npm (`node --version`, `npm --version`)
- **PostgreSQL**: 15+ (`psql --version`)
- **Git**: 2.40+ (`git --version`)
- **Windows PowerShell**

---

## Exact PowerShell Commands

### 1. Environment Configuration

From the repository root:

```powershell
# Copy environment template to .env
Copy-Item .env.example .env
```

> **Important**: `DATABASE_URL` and `TEST_DATABASE_URL` are strictly required settings with **no hard-coded defaults**. Review `.env` to verify your PostgreSQL credentials before starting servers or running tests.

---

### 2. PostgreSQL Database Setup

Create the development and test databases using `psql`:

```powershell
# Create development database
psql -U postgres -c "CREATE DATABASE university_platform;"

# Create test database
psql -U postgres -c "CREATE DATABASE university_platform_test;"
```

---

### 3. Database Migrations (Alembic)

Run database migrations to initialize or update the schema:

```powershell
Set-Location backend

# Run migrations to the latest revision
.\.venv\Scripts\alembic.exe upgrade head
```

---

### 4. Administrative User Provisioning (`scripts/create_user.py`)

Create instructor or admin accounts directly from the command line:

```powershell
# From project root
python scripts/create_user.py --email admin@example.com --password "SecureAdminPassword123!" --full-name "System Administrator" --role admin

python scripts/create_user.py --email instructor@example.com --password "InstructorPassword123!" --full-name "Prof. Turing" --role instructor
```

#### Admin Guide
1. Create the initial administrator account via CLI:
   ```powershell
   python scripts/create_user.py --email admin@example.com --password "SecurePassword123!" --full-name "Admin User" --role admin
   ```
2. Sign in at `/login` and navigate to `/admin/users` to provision instructor/admin accounts, toggle user activation statuses, or reset passwords.
3. Navigate to `/admin/organizations` to review pending organization registrations and approve or reject their publishing privileges.
4. Navigate to `/admin/internship-reviews` to inspect the moderation queue (`pending_review` by default), review full posting details alongside the organization profile, and approve or reject postings (note required on rejection). On active `open` listings, perform administrative takedowns with a mandatory justification note.

---

### 5. Backend Server Execution

Run the FastAPI development server:

```powershell
Set-Location backend

# Run with hot-reloading on port 8001
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

---

### 6. Frontend Server Execution

Run the Vite frontend development server:

```powershell
Set-Location frontend

# Start Vite development server
npm run dev
```

Frontend Routes:
- Sign in: [http://localhost:5173/login](http://localhost:5173/login)
- Register: [http://localhost:5173/register](http://localhost:5173/register)
- Course Catalogue: [http://localhost:5173/courses](http://localhost:5173/courses) (Students and Admin)
- My Courses: [http://localhost:5173/my-courses](http://localhost:5173/my-courses) (Students and Instructors)
- Create Course: [http://localhost:5173/courses/new](http://localhost:5173/courses/new) (Instructors)
- Course Details: [http://localhost:5173/courses/:id](http://localhost:5173/courses/:id)
- Edit Course: [http://localhost:5173/courses/:id/edit](http://localhost:5173/courses/:id/edit)
- Create Assignment: [http://localhost:5173/courses/:courseId/assignments/new](http://localhost:5173/courses/:courseId/assignments/new) (Instructors)
- Assignment Details: [http://localhost:5173/assignments/:id](http://localhost:5173/assignments/:id)
- Edit Assignment: [http://localhost:5173/assignments/:id/edit](http://localhost:5173/assignments/:id/edit) (Instructors)
- Grade Submission: [http://localhost:5173/assignments/:assignmentId/submissions/:submissionId/grade](http://localhost:5173/assignments/:assignmentId/submissions/:submissionId/grade) (Instructors)
- Internships Catalogue: [http://localhost:5173/internships](http://localhost:5173/internships) (Students and Admin)
- My Internships: [http://localhost:5173/my-internships](http://localhost:5173/my-internships) (Organizations)
- Create Internship: [http://localhost:5173/internships/new](http://localhost:5173/internships/new) (Organizations)
- Internship Details: [http://localhost:5173/internships/:id](http://localhost:5173/internships/:id)
- Edit Internship: [http://localhost:5173/internships/:id/edit](http://localhost:5173/internships/:id/edit) (Organizations)
- My Applications: [http://localhost:5173/my-applications](http://localhost:5173/my-applications) (Students)
- Application Details: [http://localhost:5173/applications/:id](http://localhost:5173/applications/:id) (Students, Organizations, Admin)
- User Management: [http://localhost:5173/admin/users](http://localhost:5173/admin/users) (Admin role only)
- Create User: [http://localhost:5173/admin/users/new](http://localhost:5173/admin/users/new) (Admin role only)
- Organization Approvals: [http://localhost:5173/admin/organizations](http://localhost:5173/admin/organizations) (Admin role only)
- Internship Reviews: [http://localhost:5173/admin/internship-reviews](http://localhost:5173/admin/internship-reviews) (Admin role only)
- Profile: [http://localhost:5173/profile](http://localhost:5173/profile) (Student and Organization roles)
- Account Summary &amp; Password Change: [http://localhost:5173/account](http://localhost:5173/account)
- System Status: [http://localhost:5173/status](http://localhost:5173/status) (Admin role only)

---

### 7. Linting &amp; Formatting Commands

#### Backend (Ruff)

```powershell
Set-Location backend

# Run Ruff lint check
.\.venv\Scripts\ruff.exe check .

# Run Ruff formatting check
.\.venv\Scripts\ruff.exe format --check .
```

#### Frontend (ESLint + Prettier)

```powershell
Set-Location frontend

# Run ESLint (zero warnings allowed)
npm run lint

# Check Prettier formatting
npm run format:check

# Auto-format files
npm run format
```

---

### 8. Automated Testing Commands

#### Backend Tests (Pytest)

```powershell
Set-Location backend

# Run Pytest suite
.\.venv\Scripts\pytest.exe -v
```

#### Frontend Tests (Vitest)

```powershell
Set-Location frontend

# Run Vitest suite
npm run test -- --run
```

---

## Phase 5c Definition of Done Verification

| Criteria | Status | Details |
| :--- | :---: | :--- |
| **1. Lint &amp; format pass with 0 warnings** | PASS | Ruff check &amp; format pass with 0 errors; ESLint &amp; Prettier pass with 0 warnings |
| **2. All tests pass** | PASS | Pytest (111/111 passed against real PostgreSQL); Vitest (162/162 passed across 47 test files) |
| **3. No unused files, imports, or dependencies** | PASS | All modules, imports, and packages verified clean against project guide |
| **4. Documentation is complete** | PASS | Updated README, docs/architecture.md, docs/database.md, AGENTS.md |
| **5. Working tree is clean and committed** | PASS | Small, focused conventional commits across every step |
| **6. Build verification** | PASS | Frontend production bundle builds cleanly (`tsc --noEmit && vite build`) |
| **7. File size limits** | PASS | Count physical lines with `(Get-Content <file>).Count`, including blank lines and test files. None exceeds 250 physical lines. (Reported via: `Get-ChildItem backend\app, backend\tests, frontend\src -Recurse -Include *.py,*.ts,*.tsx \| ForEach-Object { [pscustomobject]@{Lines=(Get-Content $_.FullName).Count; File=$_.Name} } \| Sort-Object Lines -Descending \| Select-Object -First 8`) |
