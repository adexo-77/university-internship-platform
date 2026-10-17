# University Learning &amp; Internship Platform &bull; Phase 0 Foundation

A production-grade, modular web platform designed for university student learning tracking, skill assessment, and internship placement matching. Built for the Brolf Tech internship technical challenge with a strict **MVP first, one phase at a time** methodology.

> **Phase 0 Status**: Foundation &amp; Tooling only. Zero business features, no domain users, no courses. Strict type safety, clean code standards, proxy verification, and test suites.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+ / 3.14+, FastAPI, SQLAlchemy 2, PostgreSQL (via `psycopg` 3), Alembic, Pydantic v2 |
| **Frontend** | React 18, Vite (with dev proxy to backend at port 8001), TypeScript (strict, no `any`), Tailwind CSS, Lucide React |
| **Testing** | Pytest + FastAPI `TestClient` (backend), Vitest + React Testing Library (frontend) |
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
│   └── architecture.md        # Phase 0 architecture and proxy topology
├── backend/
│   ├── alembic/               # Database migration environment
│   │   ├── versions/          # Migration revision scripts
│   │   └── env.py             # Migration harness wired to Base metadata
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Python dependencies
│   ├── app/
│   │   ├── core/              # Settings, database engine, exceptions
│   │   ├── models/            # SQLAlchemy 2 declarative Base
│   │   ├── schemas/           # Pydantic schemas (Health, Error)
│   │   ├── routers/           # Thin FastAPI HTTP endpoints
│   │   ├── services/          # Pure business logic and database queries
│   │   └── main.py            # FastAPI entry point & CORS
│   └── tests/
│       ├── conftest.py        # Pytest fixtures and mock DB sessions
│       └── test_health.py     # System & DB health test suite
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
        ├── api/               # API clients (fetchHealth, fetchDatabaseHealth)
        ├── components/        # HealthCheck card with rich status indicators
        ├── hooks/             # Custom hooks (useHealth)
        ├── lib/               # Utility functions (cn helper)
        ├── pages/             # HomePage presentation view
        ├── types/             # Shared TypeScript types
        ├── App.tsx            # Root application component
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

Review `.env` to verify your PostgreSQL credentials (default: `postgres:postgres@localhost:5432/university_platform`).

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

### 3. Backend Setup &amp; Run (Port 8001)

```powershell
# Navigate to backend directory
Set-Location backend

# Create virtual environment in backend/.venv (if not already created)
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations with Alembic
.\.venv\Scripts\alembic.exe upgrade head

# Start the FastAPI server on port 8001
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Backend URLs:
- API Root: [http://localhost:8001](http://localhost:8001)
- Health Check: [http://localhost:8001/health](http://localhost:8001/health) (or `/api/health`)
- Database Check: [http://localhost:8001/health/db](http://localhost:8001/health/db) (or `/api/health/db`)
- Interactive OpenAPI Docs: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### 4. Frontend Setup &amp; Run (Port 5173)

Open a second PowerShell window:

```powershell
# Navigate to frontend directory
Set-Location frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend URL:
- [http://localhost:5173](http://localhost:5173)
- API requests through Vite dev proxy: `http://localhost:5173/api/health` forwards directly to `http://localhost:8001/api/health`.

---

### 5. Linting &amp; Formatting Commands

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

### 6. Automated Testing Commands

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

## Phase 0 Definition of Done Verification

| Criteria | Status | Details |
| :--- | :---: | :--- |
| **1. Lint &amp; format pass with 0 warnings** | PASS | Ruff check &amp; format pass; ESLint &amp; Prettier pass with 0 warnings |
| **2. All tests pass** | PASS | Pytest (5/5 passed, 0 warnings); Vitest (2/2 passed) |
| **3. No unused files, imports, or dependencies** | PASS | All modules, imports, and packages verified clean |
| **4. README and docs are updated** | PASS | Full PowerShell guide, AGENTS.md, and docs/architecture.md created |
| **5. Working tree is clean and committed** | PASS | Small, focused conventional commits across all changes |
| **6. Verified both servers start** | PASS | FastAPI on 8001 and Vite on 5173 verified via proxy HTTP requests |
