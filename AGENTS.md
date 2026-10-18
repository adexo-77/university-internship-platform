# AGENTS.md &bull; Project Guidelines &amp; Architectural Rules

This document establishes the architecture, conventions, workflows, and strict rules for the **University Learning & Internship Platform** (Brolf Tech Internship Challenge). All agents, developers, and tools working on this codebase must adhere strictly to these principles across every phase.

---

## 1. Technology Stack

- **Backend**: Python 3.12+ / 3.14+ with FastAPI, SQLAlchemy 2 (ORM & 2.0 Core style), PostgreSQL with `psycopg` 3 (`psycopg[binary]`), Alembic for migrations, Pydantic v2 & `pydantic-settings`.
- **Frontend**: React 18+ with TypeScript (strict), Vite (with proxy to backend at `http://localhost:8001`), Tailwind CSS, Lucide React.
- **Testing & Tooling**:
  - Backend: Pytest, FastAPI `TestClient`, Ruff (`ruff check`, `ruff format`).
  - Frontend: Vitest, React Testing Library, ESLint 9 (flat config), Prettier.
- **Environment & Platform**: Windows PowerShell compatibility, no hard-coded Windows paths, Unix LF line endings across all files (`.gitattributes`).

---

## 2. Project Structure Guide

The official **PROJECT STRUCTURE GUIDE** outlines the file tree and structural conventions across all phases:

```text
university-internship-platform/
├── .editorconfig              # Editor consistency rules (LF, UTF-8, indentation)
├── .env.example               # Template environment configuration
├── .gitattributes             # Enforce LF line endings (* text=auto eol=lf)
├── .gitignore                 # Ignore .env, .venv, node_modules, dist, __pycache__, etc.
├── AGENTS.md                  # Project constitution and multi-phase agent guidelines
├── README.md                  # Setup instructions, exact PowerShell commands
├── docs/                      # Architectural designs, schemas, and specifications
│   ├── architecture.md        # Architecture topology and endpoint matrix
│   ├── database.md            # Mermaid ER diagram and schema specifications
│   └── design.md              # Design system tokens, components, and UX rules
├── scripts/                   # CLI administrative and automation tools
│   └── create_user.py         # Administrative user provisioning script
├── backend/
│   ├── alembic/               # Database migration environment
│   │   ├── versions/          # Alembic revision migration files
│   │   │   ├── 6d7757d439a5_create_users_and_sessions_tables.py
│   │   │   └── d5196328fe27_create_student_and_organization_profiles.py
│   │   ├── env.py             # Migration harness wired to Base metadata
│   │   └── script.py.mako     # Migration template
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development & testing tools (ruff, pytest, httpx)
│   ├── app/
│   │   ├── core/              # Config, database engine, security helpers, deps, exceptions
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── deps.py
│   │   │   ├── exceptions.py
│   │   │   └── security.py
│   │   ├── models/            # SQLAlchemy declarative models
│   │   │   ├── base.py
│   │   │   ├── organization_profile.py
│   │   │   ├── session.py
│   │   │   ├── student_profile.py
│   │   │   └── user.py
│   │   ├── schemas/           # Pydantic validation schemas
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   ├── organization_profile.py
│   │   │   └── student_profile.py
│   │   ├── routers/           # Thin FastAPI HTTP endpoints (/api only)
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   ├── organization_profile.py
│   │   │   └── student_profile.py
│   │   ├── services/          # Pure business logic and domain rules
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   ├── organization_profile.py
│   │   │   └── student_profile.py
│   │   └── main.py            # FastAPI app initialization and middleware
│   └── tests/                 # Pytest test suite mirroring app/ domain modules
│       ├── conftest.py        # Database harness and fixtures
│       ├── test_auth_login.py # Auth login, invalid credentials & hash leak tests
│       ├── test_auth_register.py # Registration & atomic profile provisioning tests
│       ├── test_auth_session.py  # Session lifecycle, logout, expiry & role guard tests
│       ├── test_health.py     # Health integration tests (mirrors health.py)
│       ├── test_organization_profile.py # Organization profile integration tests
│       ├── test_script_create_user.py   # CLI user creation script tests
│       └── test_student_profile.py      # Student profile integration tests
└── frontend/
    ├── .prettierrc            # Prettier code formatting config
    ├── eslint.config.js       # ESLint 9 flat configuration
    ├── index.html             # Single-page HTML entry with typography and SEO metadata
    ├── package.json           # Frontend dependencies and npm scripts
    ├── package-lock.json      # Locked npm dependency tree
    ├── postcss.config.js      # PostCSS configuration
    ├── tailwind.config.js     # Tailwind CSS design system tokens
    ├── tsconfig.json          # Strict TypeScript compiler options
    ├── tsconfig.node.json     # Vite config TypeScript setup
    ├── vite.config.ts         # Vite configuration with /api proxy to :8001 and Vitest
    └── src/
        ├── api/               # API clients and HTTP request wrappers
        │   ├── auth.ts
        │   ├── health.ts
        │   └── profile.ts
        ├── components/
        │   ├── layout/        # Application shell and structural layout
        │   │   ├── AppShell.tsx
        │   │   └── AppShell.test.tsx
        │   ├── profile/       # Role-specific profile form components
        │   │   ├── OrganizationProfileForm.tsx
        │   │   ├── OrganizationProfileForm.test.tsx
        │   │   ├── StudentProfileForm.tsx
        │   │   └── StudentProfileForm.test.tsx
        │   ├── routes/        # Navigation route guards
        │   │   ├── ProtectedRoute.tsx
        │   │   ├── RoleRoute.tsx
        │   │   └── RouteGuards.test.tsx
        │   ├── ui/            # Reusable, typed UI components (Button, Badge, etc.)
        │   │   ├── Badge.tsx
        │   │   ├── Button.tsx
        │   │   ├── DataTable.tsx
        │   │   ├── EmptyState.tsx
        │   │   ├── ErrorMessage.tsx
        │   │   ├── Notice.tsx
        │   │   ├── PageHeader.tsx
        │   │   ├── Select.tsx
        │   │   ├── TextField.tsx
        │   │   ├── Textarea.tsx
        │   │   └── index.ts
        │   ├── HealthCheck.tsx
        │   └── HealthCheck.test.tsx
        ├── config/            # Centralized configuration
        │   └── navigation.ts
        ├── context/           # React context providers
        │   ├── AuthContext.tsx
        │   ├── AuthContext.test.tsx
        │   └── auth-context-def.ts
        ├── hooks/             # Custom React hooks
        │   ├── useAuth.ts
        │   └── useHealth.ts
        ├── lib/               # Utility libraries (cn, skills parsing)
        │   ├── cn.ts
        │   ├── skills.ts
        │   └── skills.test.ts
        ├── pages/             # Page-level route views
        │   ├── AccountPage.tsx
        │   ├── LoginPage.tsx
        │   ├── LoginPage.test.tsx
        │   ├── NotFoundPage.tsx
        │   ├── ProfilePage.tsx
        │   ├── ProfilePage.test.tsx
        │   ├── RegisterPage.tsx
        │   ├── RegisterPage.test.tsx
        │   └── SystemStatusPage.tsx
        ├── test/              # Frontend testing setup
        │   └── setup.ts
        ├── types/             # Shared TypeScript type definitions
        │   ├── auth.ts
        │   ├── health.ts
        │   └── profile.ts
        ├── App.tsx            # Main router configuration
        ├── index.css          # Global styles and design system tokens
        └── main.tsx           # React entry point
```

### Structure Rules for Every Future Phase

- New code goes in the folder that matches its job. Business logic lives in services, never in routers.
- Models: one file per model. Schemas, routers, services and tests: one file per domain, with the same name across them (for example `course.py`).
- Each file has one job and stays under about 300 lines. Split before it grows past that.
- No files named `utils` or `helpers` that collect unrelated code.
- No scratch, backup, debug or unused files. Only source and docs are committed.
- Each phase updates README, docs/database.md and docs/architecture.md when it changes them.
- Before finishing any phase, run `git ls-files` and compare it to this guide.

---

## 3. How to Run and Test (Windows PowerShell)

### Backend

```powershell
# From project root
Set-Location backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run backend development server (port 8001)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Run linter and formatting checks
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .

# Run tests
.\.venv\Scripts\pytest.exe -v
```

### Frontend

```powershell
# From project root
Set-Location frontend

# Run frontend development server (port 5173)
npm run dev

# Run linter and formatting checks
npm run lint
npm run format:check

# Run tests
npm run test
```

---

## 4. Mandatory Architectural Rules for Every Future Phase

1. **Server Session Identity**:
   Identity always comes from the server session (or validated token decoded on the server), **never** from the request body or client headers. The client cannot forge or specify its own user identity.
2. **Server-Side Role Checks**:
   Role checks (e.g., student, supervisor, company mentor, admin) happen exclusively on the server. UI-level visibility controls are purely convenience layers.
3. **Comprehensive Endpoint Testing**:
   Every endpoint must have automated tests covering both the happy path and permission/validation failures.
4. **Alembic Migrations for Every Model Change**:
   Every change or addition to SQLAlchemy models must be accompanied by an Alembic migration script in `backend/alembic/versions/`.
5. **Thin Routers, Business Logic in Services**:
   Routers only handle request parsing, parameter injection, status codes, and response serialization. All database interactions and domain logic live inside `backend/app/services/`.
6. **File Size Limit**:
   Keep all source files under approximately 300 lines. Split into focused sub-modules when complexity grows.
7. **Strict Typing Everywhere**:
   - Python: Complete type hints on all functions, parameters, return types, and variables.
   - TypeScript: Strict compiler options enabled. Absolute prohibition of the `any` type (`@typescript-eslint/no-explicit-any` is configured as an error).
8. **Clean Code Hygiene**:
   No dead code, no commented-out code, no temporary debug files, no duplicated logic, and no magic numbers (use named constants or enums).
9. **Consistent API Error Format & Status Codes**:
   Use consistent HTTP status codes (200, 201, 400, 401, 403, 404, 409, 422, 500, 503) and consistent error bodies:
   ```json
   {
     "detail": "Descriptive message",
     "code": "MACHINE_READABLE_CODE"
   }
   ```
10. **Conventional, Focused Commits**:
    Commit messages must use standard conventional commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`) and be small, focused, and verified before committing.
11. **Strict Phase Discipline**:
    Never touch or implement code outside the active phase. Build Phase 0 foundation first, then progress phase by phase without premature feature bloat.

---

## 5. Definition of Done

Every phase, feature, or refactoring task must satisfy the following checklist before completion:

1. **Lint and format pass with 0 warnings** (`ruff check .`, `ruff format --check .`, `npm run lint`, `npm run format:check`).
2. **All tests pass** (`pytest -v`, `npm run test`).
3. **No unused files, imports, or dependencies**.
4. **Documentation is complete** (`README.md`, `docs/architecture.md`, `docs/database.md`, `docs/design.md`).
5. **Working tree is clean and committed** with small, focused conventional commits.
6. **Report the 8 largest source files by line count; none may exceed 300 lines.**

