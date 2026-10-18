# University Learning &amp; Internship Platform &bull; Phase 5 Internship Postings &amp; Applications

A production-grade, modular web platform designed for university student learning tracking, skill assessment, and internship placement matching. Built for the Brolf Tech internship technical challenge with a strict **MVP first, one phase at a time** methodology.

> **Phase 5 Status**: Internship postings and applications fully operational. Organization internship posting creation with future application deadlines, posting lifecycle transitions (`draft` -> `open` -> `closed`), student and admin searchable catalogue with keyword search and work mode filters, student application submission with cover letter, profile completeness validation (university and department required), duplicate prevention, withdrawal capability, organization applicant background profile and cover letter review, decision workflow (`shortlisted`, `accepted`, `rejected`) with feedback messages, terminal state locks, and role-based access control.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+ / 3.14+, FastAPI, SQLAlchemy 2, PostgreSQL (via `psycopg` 3), Alembic, Pydantic v2 |
| **Frontend** | React 18, React Router 6/7, Vite (proxy to backend :8001), TypeScript (strict, no `any`), Tailwind CSS, Lucide React |
| **Testing** | Pytest + FastAPI `TestClient` (backend: 86 tests), Vitest + React Testing Library (frontend: 120 tests) |
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
│   ├── database.md            # Mermaid ER diagram and schema specifications
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
│   │   │   └── e17d6f716230_create_internship_postings_and_.py
│   │   └── env.py             # Migration harness wired to Base metadata
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development and testing dependencies (pytest, ruff, httpx)
│   ├── app/
│   │   ├── core/              # Settings, database engine, security helpers, deps
│   │   ├── models/            # SQLAlchemy models (user, session, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application)
│   │   ├── schemas/           # Pydantic schemas (auth, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application, health)
│   │   ├── routers/           # Thin FastAPI HTTP endpoints (/api only: auth, student_profile, organization_profile, course, enrollment, assignment, submission, internship, application, health)
│   │   ├── services/          # Pure business logic and domain rules (auth, student_profile, organization_profile, course, course_catalog, enrollment, assignment, submission, internship, internship_catalog, application, health)
│   │   └── main.py            # FastAPI entry point & CORS
│   └── tests/
│       ├── conftest.py        # Pytest fixtures and database test harnesses
│       ├── factories.py       # Test data factories and authentication helpers
│       ├── test_application_apply.py    # Application submission, profile prerequisite, and withdrawal tests
│       ├── test_application_decision.py # Organization application review, decision transitions, and locking tests
│       ├── test_assignment_create.py    # Assignment creation and visibility tests
│       ├── test_assignment_lifecycle.py # Assignment grade floor and deletion guard tests
│       ├── test_auth_login.py           # Auth login tests
│       ├── test_auth_register.py        # Auth registration tests
│       ├── test_auth_session.py         # Session lifecycle & role guard tests
│       ├── test_course_create.py        # Course creation permissions and field validation tests
│       ├── test_course_update.py        # Course update and status transition tests
│       ├── test_course_visibility.py    # Course visibility, catalog search, and pagination tests
│       ├── test_enrollment.py           # Enrollment, roster inspection, and cascade delete tests
│       ├── test_health.py               # System & DB health test suite
│       ├── test_internship_catalog.py   # Internship catalogue search, work mode filters, and visibility tests
│       ├── test_internship_manage.py    # Internship creation, owner editing, and status transition tests
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
        ├── api/               # API clients (auth, health, profile, course, assignment, internship, application)
        ├── components/
        │   ├── assignments/   # AssignmentForm, AssignmentTable, CourseAssignmentsSection, DueBadge, GradeForm, SubmissionForm, SubmissionStatusBadge, SubmissionsTable
        │   ├── courses/       # CourseForm, CourseTable, EnrollButton, StudentRosterTable
        │   ├── internships/   # InternshipForm, InternshipTable, InternshipStatusBadge, ApplyForm, ApplicationStatusBadge, ApplicantsTable, DecisionForm, MyApplicationsTable, StudentApplicationPanel, InternshipApplicantsSection
        │   ├── layout/        # AppShell layout component
        │   ├── profile/       # StudentProfileForm, OrganizationProfileForm
        │   ├── routes/        # ProtectedRoute, RoleRoute
        │   └── ui/            # Reusable UI component library (Button, TextField, DataTable, etc.)
        ├── config/            # Centralized navigation configuration
        ├── context/           # React AuthContext and AuthProvider
        ├── hooks/             # Custom hooks (useAuth, useHealth, usePageTitle)
        ├── lib/               # Utility functions (cn, dates, skills)
        ├── pages/             # Pages (Login, Register, Account, Profile, Courses, MyCourses, CourseCreate, CourseEdit, CourseDetail, AssignmentCreate, AssignmentEdit, AssignmentDetail, SubmissionGrade, Internships, InternshipCreate, InternshipEdit, InternshipDetail, MyInternships, MyApplications, ApplicationDetail, SystemStatus, NotFound)
        ├── types/             # Shared TypeScript types (auth, health, profile, course, assignment, internship, application)
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
- Profile: [http://localhost:5173/profile](http://localhost:5173/profile) (Student and Organization roles)
- Account Summary: [http://localhost:5173/account](http://localhost:5173/account)
- System Status: [http://localhost:5173/status](http://localhost:5173/status) (Admin role only)

---

### 7. Linting & Formatting Commands

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

## Phase 4 Definition of Done Verification

| Criteria | Status | Details |
| :--- | :---: | :--- |
| **1. Lint & format pass with 0 warnings** | PASS | Ruff check & format pass with 0 errors; ESLint & Prettier pass with 0 warnings |
| **2. All tests pass** | PASS | Pytest (58/58 passed against real PostgreSQL); Vitest (78/78 passed across 22 test files) |
| **3. No unused files, imports, or dependencies** | PASS | All modules, imports, and packages verified clean against project guide |
| **4. Documentation is complete** | PASS | Updated README, docs/architecture.md, docs/database.md, AGENTS.md |
| **5. Working tree is clean and committed** | PASS | Small, focused conventional commits across every step |
| **6. Build verification** | PASS | Frontend production bundle builds cleanly (`tsc --noEmit && vite build`) |
| **7. File size limits** | PASS | Count physical lines with `(Get-Content <file>).Count`, including blank lines and test files. From now on, any file above 250 physical lines must be split before the phase is called done. (Reported via: `Get-ChildItem backend\app, backend\tests, frontend\src -Recurse -Include *.py,*.ts,*.tsx \| ForEach-Object { [pscustomobject]@{Lines=(Get-Content $_.FullName).Count; File=$_.Name} } \| Sort-Object Lines -Descending \| Select-Object -First 8`) |
