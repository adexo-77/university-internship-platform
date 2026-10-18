# University Learning &amp; Internship Platform &bull; Phase 1 Authentication &amp; Roles

A production-grade, modular web platform designed for university student learning tracking, skill assessment, and internship placement matching. Built for the Brolf Tech internship technical challenge with a strict **MVP first, one phase at a time** methodology.

> **Phase 1 Status**: Authentication and role-based access control fully operational. Models and migrations for users and sessions, stdlib `scrypt` hashing, constant-time authentication timing defense, HttpOnly cookies, client route guards, and admin CLI tools.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+ / 3.14+, FastAPI, SQLAlchemy 2, PostgreSQL (via `psycopg` 3), Alembic, Pydantic v2 |
| **Frontend** | React 18, React Router 6/7, Vite (proxy to backend :8001), TypeScript (strict, no `any`), Tailwind CSS, Lucide React |
| **Testing** | Pytest + FastAPI `TestClient` (backend: 21 tests), Vitest + React Testing Library (frontend: 22 tests) |
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
│   │   └── env.py             # Migration harness wired to Base metadata
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development and testing dependencies (pytest, ruff, httpx)
│   ├── app/
│   │   ├── core/              # Settings, database engine, security helpers, deps
│   │   ├── models/            # SQLAlchemy 2 declarative models (User, Session)
│   │   ├── schemas/           # Pydantic schemas (Auth, Health, Errors)
│   │   ├── routers/           # Thin FastAPI HTTP endpoints (/api only)
│   │   ├── services/          # Pure business logic and domain rules
│   │   └── main.py            # FastAPI entry point & CORS
│   └── tests/
│       ├── conftest.py        # Pytest fixtures and database test harnesses
│       ├── test_auth.py       # Authentication, security, and role tests
│       ├── test_health.py     # System & DB health test suite
│       └── test_script_create_user.py # CLI script integration tests
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
        ├── api/               # API clients (auth, health)
        ├── components/        # Layout (AppShell), RouteGuards, and UI library
        ├── config/            # Centralized navigation configuration
        ├── context/           # React AuthContext and AuthProvider
        ├── hooks/             # Custom hooks (useAuth, useHealth)
        ├── lib/               # Utility functions (cn helper)
        ├── pages/             # Pages (Login, Register, Account, SystemStatusPage, NotFound)
        ├── types/             # Shared TypeScript types
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
# From project root (using the backend venv python)
.\backend\.venv\Scripts\python.exe scripts/create_user.py --email admin@university.edu --name "Platform Administrator" --role admin

# Create an instructor
.\backend\.venv\Scripts\python.exe scripts/create_user.py --email instructor@university.edu --name "Dr. Alan Turing" --role instructor
```

> **Security Note**: Password entry uses Python's standard `getpass` module. Passwords are never passed as CLI arguments, stored in shell history, or printed to terminal logs. Running the command again with an existing email prevents duplicates.

---

### 5. Backend Setup &amp; Run (Port 8001)

```powershell
# Navigate to backend directory
Set-Location backend

# Create virtual environment in backend/.venv (if not already created)
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt       # Production dependencies
pip install -r requirements-dev.txt   # Development & testing tools (ruff, pytest, httpx)

# Run database migrations
.\.venv\Scripts\alembic.exe upgrade head

# Start the FastAPI server on port 8001
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Backend URLs:
- API Root: [http://localhost:8001](http://localhost:8001)
- Interactive OpenAPI Docs: [http://localhost:8001/docs](http://localhost:8001/docs)
- Endpoints:
  - `POST /api/auth/register` (student, organization)
  - `POST /api/auth/login`
  - `POST /api/auth/logout`
  - `GET /api/auth/me`
  - `GET /api/health`
  - `GET /api/health/db`

---

### 6. Frontend Setup &amp; Run (Port 5173)

Open a second PowerShell window:

```powershell
# Navigate to frontend directory
Set-Location frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend Routes:
- Sign in: [http://localhost:5173/login](http://localhost:5173/login)
- Register: [http://localhost:5173/register](http://localhost:5173/register)
- Account Profile: [http://localhost:5173/account](http://localhost:5173/account)
- System Status: [http://localhost:5173/](http://localhost:5173/) (Admin role only)

---

### 7. Linting &amp; Formatting Commands

#### Backend (Ruff)

```powershell
Set-Location backend

# Run Ruff lint check
.\.venv\Scripts\ruff.exe check .

# Run Ruff formatting check
.\.venv\Scripts\ruff.exe format --check .

# To automatically apply fixes:
.\.venv\Scripts\ruff.exe check --fix .
.\.venv\Scripts\ruff.exe format .
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
npm run test
```

---

## Phase 1 Definition of Done Verification

| Criteria | Status | Details |
| :--- | :---: | :--- |
| **1. Lint &amp; format pass with 0 warnings** | PASS | Ruff check &amp; format pass; ESLint &amp; Prettier pass with 0 warnings |
| **2. All tests pass** | PASS | Pytest (21/21 passed, 0 warnings); Vitest (22/22 passed) |
| **3. No unused files, imports, or dependencies** | PASS | All modules, imports, and packages verified clean |
| **4. Documentation is complete** | PASS | Updated README, docs/architecture.md, docs/database.md, and docs/design.md |
| **5. Working tree is clean and committed** | PASS | Small, focused conventional commits across every step |
| **6. Build verification** | PASS | Frontend production bundle builds cleanly (`tsc --noEmit && vite build`) |
