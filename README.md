# University Learning &amp; Internship Platform &bull; Phase 7b Developer Setup, Demo Data &amp; CI

[![CI](https://github.com/adexo-77/university-internship-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/adexo-77/university-internship-platform/actions/workflows/ci.yml)

A production-grade, modular web platform designed for university student learning tracking, skill assessment, and internship placement matching. Built for the Brolf Tech internship technical challenge with a strict **MVP first, one phase at a time** methodology.

---

## Quick Start

Get up and running locally in four commands:

### 1. Clone the Repository
```powershell
git clone https://github.com/adexo-77/university-internship-platform.git
Set-Location university-internship-platform
```

### 2. Run Automated Setup &amp; Seed
```powershell
python scripts/setup_dev.py --seed
```
*Creates the virtualenv, installs Python &amp; Node dependencies, provisions development &amp; test databases, applies Alembic migrations, and populates the rich demo dataset.*

### 3. Start Backend Server (:8001)
```powershell
Set-Location backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 4. Start Frontend Client (:5173)
```powershell
# In a separate PowerShell window
Set-Location frontend
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) to explore the platform.

---

## Demo Accounts &amp; Capabilities

All demo accounts share a single constant password for easy local evaluation:
> **DEMO PASSWORD (DEMO ONLY)**: `DemoPassword123!`

| Role | Email | Profile State | What This Account Demonstrates |
| :--- | :--- | :--- | :--- |
| **Admin** | `demo.admin@example.com` | Complete | Platform administration dashboard, user provisioning &amp; password resets, organization registration approvals, internship moderation review queue, and administrative listing takedowns. |
| **Instructor** | `demo.instructor@example.com` | Complete | Instructor dashboard, course authoring &amp; publishing (active and draft courses), assignment creation with deadlines, and student submission grading queue. |
| **Student (Ready)** | `demo.student@example.com` | Complete | Student dashboard, enrolled course tracking, assignments due soon (due in 2 days, 3 weeks, past due), recent grade cards, internship catalog search, and submitted applications. |
| **Student (New)** | `demo.student2@example.com` | Incomplete | Incomplete profile demonstration showing the profile completion banner and prerequisite guard blocking internship applications until bio &amp; skills are saved. |
| **Organization (Approved)** | `demo.org@example.com` | Approved | Organization dashboard, internship postings across all lifecycles (`open`, `pending_review`, `draft`, `rejected`, `closed`), and applicant decision workflows (shortlist, accept, reject). |
| **Organization (Pending)** | `demo.neworg@example.com` | Pending Review | Pending approval banner demonstration, with internship creation disabled until platform administrator reviews and approves the company profile. |

---

## Network Ports &amp; Services

| Port | Service | Description | URL |
| :--- | :--- | :--- | :--- |
| **5173** | **Frontend Client** | Vite React Single-Page Application | [http://localhost:5173](http://localhost:5173) |
| **8001** | **Backend API** | FastAPI REST Application | [http://localhost:8001/api](http://localhost:8001/api) |
| **8001** | **API Documentation** | Interactive Swagger OpenAPI Docs | [http://localhost:8001/docs](http://localhost:8001/docs) |
| **8001** | **Health DB Check** | Database connectivity probe | [http://localhost:8001/api/health/db](http://localhost:8001/api/health/db) |
| **5432** | **PostgreSQL** | Primary Relational Database Engine | `localhost:5432` |

---

## Troubleshooting

### PostgreSQL Connection &amp; Authentication Errors
- **Issue**: `setup_dev.py` fails with `password authentication failed for user "postgres"`.
- **Fix**: Verify your PostgreSQL server service is running (`Get-Service postgresql*`). When prompted by `setup_dev.py`, enter your actual local PostgreSQL `postgres` user password. Special characters (such as `@`, `!`, `#`) are automatically URL-encoded for the SQLAlchemy connection URI.
- **Manual Check**: Test connectivity directly with `psql -U postgres -h localhost`.

### Port Conflicts (:8001 or :5173 Already in Use)
- **Issue**: `Address already in use` error when starting FastAPI or Vite.
- **Fix**: Check running processes on those ports:
  ```powershell
  Get-NetTCPConnection -LocalPort 8001,5173 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess
  ```
  Terminate lingering processes using `Stop-Process -Id <OwningProcess> -Force`.

### Node.js or Python Version Warnings
- **Prerequisites**: Python 3.12+ (or 3.14+) and Node.js 20+ (or 24+ LTS) are required.
- Run `python --version` and `node --version` to ensure modern runtime versions are active on your `PATH`.

### Resetting Dev Database &amp; Re-seeding
- To start from a completely clean slate at any time:
  ```powershell
  psql -U postgres -c "DROP DATABASE IF EXISTS university_platform WITH (FORCE);"
  psql -U postgres -c "DROP DATABASE IF EXISTS university_platform_test WITH (FORCE);"
  python scripts/setup_dev.py --seed
  ```

---

## Docker Status Note

During environment evaluation:
- Docker CLI was detected on host (`docker --version` output: `Docker version 29.8.2, build 7fc2dff`).
- However, Docker Desktop daemon is not running and WSL 2 has no installed Linux engine on this Windows environment (`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`).
- In strict adherence to Phase 7b item 4 instructions (*"Docker, ONLY if `docker --version` works on this machine so you can test it; if Docker is not installed, skip this item, say so plainly, and do not write untested Docker files"*), container runtime configuration was cleanly skipped to prevent introducing untested Docker artifacts.
- The platform is fully runnable, testable, and verified via native Python/Node tooling through `scripts/setup_dev.py`.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+ / 3.14+, FastAPI, SQLAlchemy 2, PostgreSQL (via `psycopg` 3), Alembic, Pydantic v2 |
| **Frontend** | React 18, React Router 6/7, Vite (proxy to backend :8001), TypeScript (strict, no `any`), Tailwind CSS, Lucide React |
| **Testing** | Pytest + FastAPI `TestClient` (backend: 190 tests), Vitest + React Testing Library (frontend: 207 tests across 60 files) |
| **Tooling &amp; Quality** | Ruff (backend lint &amp; format), ESLint 9 + Prettier (frontend lint &amp; format), `pip-audit`, `npm audit` |
| **CI / CD** | GitHub Actions (`.github/workflows/ci.yml`): backend matrix, frontend matrix, and fresh migration check |
| **Environment** | Windows PowerShell compatible, Unix LF line endings, no hardcoded Windows paths |

---

## Directory Structure

```text
university-internship-platform/
├── .editorconfig              # Editor consistency rules (LF, UTF-8, indentation)
├── .env.example               # Template environment configuration
├── .gitattributes             # Enforce LF line endings (* text=auto eol=lf)
├── .gitignore                 # Excludes .env, .venv, node_modules, dist, __pycache__, etc.
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI matrix (backend, frontend, migrations)
├── AGENTS.md                  # Project constitution & strict architectural guidelines
├── README.md                  # Setup instructions and PowerShell commands
├── docs/
│   ├── architecture.md        # Architecture, topology, and endpoint contracts
│   ├── database.md            # Mermaid ER diagram, status lifecycle diagram, and schema specifications
│   ├── design.md              # Design tokens, components, and layout guidelines
│   └── security.md            # Threat model, controls matrix, and security guidelines
├── scripts/
│   ├── create_user.py         # CLI administrative user provisioning tool
│   ├── seed_demo.py           # Idempotent demo dataset seeder
│   ├── seed_demo_academics.py # Courses, assignments, submissions seed logic
│   ├── seed_demo_internships.py # Internships, applications seed logic
│   ├── seed_demo_users.py     # Demo users and profile seeding logic
│   ├── setup_dev.py           # Cross-platform developer environment setup
│   └── setup_dev_db.py        # Database creation and URL helpers for setup
├── backend/
│   ├── alembic/               # Database migration environment
│   │   ├── versions/          # Migration revision scripts
│   │   └── env.py             # Migration harness wired to Base metadata
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development and testing dependencies (pytest, ruff, httpx)
│   ├── app/
│   │   ├── core/              # Settings, database engine, security helpers, deps
│   │   ├── models/            # SQLAlchemy declarative models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # Thin FastAPI HTTP endpoints (/api only)
│   │   ├── services/          # Pure business logic and domain rules
│   │   └── main.py            # FastAPI entry point & middleware
│   └── tests/                 # Comprehensive Pytest test suite (190 tests)
└── frontend/
    ├── eslint.config.js       # ESLint 9 flat configuration
    ├── index.html             # HTML entry with typography and SEO metadata
    ├── package.json           # Frontend dependencies and npm scripts
    ├── postcss.config.js      # PostCSS config
    ├── tailwind.config.js     # Tailwind CSS theme setup
    ├── tsconfig.json          # Strict TypeScript configuration
    ├── tsconfig.node.json     # Vite config TypeScript options
    ├── vite.config.ts         # Vite proxy configuration (/api -> :8001) and Vitest
    └── src/                   # React TypeScript application (207 tests across 60 test suites)
```

---

## Automated Developer Setup (`scripts/setup_dev.py`)

Run the cross-platform setup script from the repository root:

```powershell
# Standard setup: venv, dependencies, .env, databases, and migrations
python scripts/setup_dev.py

# Or setup and populate full demo dataset:
python scripts/setup_dev.py --seed
```

### Manual Setup Fallback

If you prefer to configure manually:

1. **Environment Configuration**:
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

2. **Database Provisioning**:
   ```powershell
   psql -U postgres -c "CREATE DATABASE university_platform;"
   psql -U postgres -c "CREATE DATABASE university_platform_test;"
   ```

3. **Virtualenv &amp; Dependencies**:
   ```powershell
   python -m venv backend/.venv
   .\backend\.venv\Scripts\Activate.ps1
   pip install -r backend/requirements.txt -r backend/requirements-dev.txt
   Set-Location frontend; npm install; Set-Location ..
   ```

4. **Migrations &amp; Seed**:
   ```powershell
   Set-Location backend; .\.venv\Scripts\alembic.exe upgrade head; Set-Location ..
   python scripts/seed_demo.py
   ```

---

## Administrative User Provisioning (`scripts/create_user.py`)

Create instructor or admin accounts directly from the command line:

```powershell
# From project root
python scripts/create_user.py --email admin@example.com --password "SecureAdminPassword123!" --full-name "System Administrator" --role admin

python scripts/create_user.py --email instructor@example.com --password "InstructorPassword123!" --full-name "Prof. Turing" --role instructor
```

---

## Linting &amp; Formatting Commands

### Backend (Ruff)

```powershell
Set-Location backend

# Run Ruff lint check
.\.venv\Scripts\ruff.exe check .

# Run Ruff formatting check
.\.venv\Scripts\ruff.exe format --check .
```

### Frontend (ESLint + Prettier)

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

## Automated Testing Commands

### Backend Tests (Pytest)

```powershell
Set-Location backend

# Run Pytest suite
.\.venv\Scripts\pytest.exe -v
```

### Frontend Tests (Vitest)

```powershell
Set-Location frontend

# Run Vitest suite
npm run test
```

---

## Phase 7b Definition of Done Verification

| Criteria | Status | Details |
| :--- | :---: | :--- |
| **1. Lint &amp; format pass with 0 warnings** | PASS | Ruff check &amp; format pass with 0 errors; ESLint &amp; Prettier pass with 0 warnings |
| **2. All tests pass** | PASS | Pytest (190/190 passed against real PostgreSQL); Vitest (207/207 passed across 60 test files) |
| **3. Clean Clone Proof** | PASS | Cloned into isolated directory, executed `setup_dev.py --seed`, verified all 6 demo accounts &amp; dashboards return 200 |
| **4. Idempotent Demo Seeder** | PASS | `scripts/seed_demo.py` safely runs repeatedly without duplicating records; refuses in production |
| **5. Cross-Platform Setup Script** | PASS | `scripts/setup_dev.py` checks versions, provisions venv/node_modules, handles hidden password input, runs migrations |
| **6. Continuous Integration** | PASS | `.github/workflows/ci.yml` runs backend matrix, frontend matrix, and migration schema drift check |
| **7. No unused files, imports, or dependencies** | PASS | All modules, imports, and packages verified clean against project guide |
| **8. Documentation is complete** | PASS | Updated `README.md` with Quick start, Demo accounts table, ports, troubleshooting, and Docker note |
| **9. Working tree is clean and committed** | PASS | Small, focused conventional commits across every step |
| **10. File size limits** | PASS | All source and test files strictly under 250 physical lines |
