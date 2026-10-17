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

## 2. Repository & Folder Structure

```text
university-internship-platform/
├── .editorconfig              # Editor consistency rules (LF, UTF-8, indentation)
├── .env.example               # Template environment configuration
├── .gitattributes             # Enforce LF line endings (* text=auto eol=lf)
├── .gitignore                 # Ignore .env, .venv, node_modules, dist, __pycache__, etc.
├── AGENTS.md                  # Project constitution and multi-phase agent guidelines
├── README.md                  # Setup instructions, exact PowerShell commands
├── docs/                      # Architectural designs, schemas, and specifications
│   └── architecture.md
├── backend/
│   ├── alembic/               # Database migration environment and versions
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Ruff and Pytest settings
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development & testing tools (ruff, pytest, httpx)
│   ├── app/
│   │   ├── core/              # Config, database engine, exceptions
│   │   ├── models/            # SQLAlchemy declarative models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # Thin FastAPI HTTP endpoints
│   │   ├── services/          # Pure business logic and domain rules
│   │   └── main.py            # FastAPI app initialization and middleware
│   └── tests/                 # Pytest test suite with TestClient
└── frontend/
    ├── eslint.config.js       # ESLint 9 flat configuration
    ├── index.html             # Single-page HTML entry with SEO metadata
    ├── package.json           # Frontend dependencies and npm scripts
    ├── postcss.config.js      # PostCSS configuration
    ├── tailwind.config.js     # Tailwind CSS design system
    ├── tsconfig.json          # Strict TypeScript compiler options
    ├── tsconfig.node.json     # Vite config TypeScript setup
    ├── vite.config.ts         # Vite configuration with /api proxy to :8001 and Vitest
    └── src/
        ├── api/               # API clients and HTTP request wrappers
        ├── components/        # Reusable, typed UI components
        ├── hooks/             # Custom React hooks
        ├── lib/               # Utility functions and helpers
        ├── pages/             # Page-level route views
        ├── types/             # Shared TypeScript type definitions
        └── main.tsx           # React entry point
```

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
