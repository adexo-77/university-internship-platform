# Platform Architecture &bull; Authentication, Roles, Profiles, Courses &amp; Enrollment

## 1. Overview

The **University Learning & Internship Platform** is engineered with a modular, decoupled architecture prioritizing maintainability, strict typing, and high reliability.

- **Phase 1**: Authentication, session lifecycle, and role-based access control across four primary roles: `student`, `instructor`, `organization`, and `admin`.
- **Phase 2**: Domain profile management:
  - **Student profiles**: academic tracking (university, department, year of study 1-6), bio, and skill inventory.
  - **Organization profiles**: enterprise representation (company name, industry, location, verified website URL, description).
  - **Atomic transactions**: registration automatically creates the role-appropriate profile row in the same transaction.
- **Phase 3**: Courses and Enrollment:
  - **Courses**: instructor-authored learning syllabi with draft/published lifecycle.
  - **Enrollment**: student enrollment and unenrollment in published courses with unique constraints.
  - **Rosters**: instructor and admin visibility into enrolled student names, emails, and enrollment dates.
  - **Discovery**: title search and limit/offset pagination with per-student enrollment flags.

```mermaid
flowchart TD
    subgraph Browser ["Client Browser"]
        SPA["React SPA (Port 5173)"]
        CookieStorage["HttpOnly Cookie (session_token)"]
    end

    subgraph ViteServer ["Vite Development Server"]
        Proxy["Vite Proxy (/api -> :8001)"]
    end

    subgraph BackendApp ["FastAPI Backend (Port 8001)"]
        AuthRouter["AuthRouter (/api/auth/*)"]
        StudentRouter["StudentProfileRouter (/api/students/*)"]
        OrgRouter["OrganizationProfileRouter (/api/organizations/*)"]
        CourseRouter["CourseRouter (/api/courses/*)"]
        EnrollmentRouter["EnrollmentRouter (/api/courses/{id}/enrollment & roster)"]
        Deps["Dependencies (get_current_user, require_roles)"]
        AuthService["AuthService"]
        StudentService["StudentProfileService"]
        OrgService["OrganizationProfileService"]
        CourseService["CourseService"]
        EnrollmentService["EnrollmentService"]
        Security["Security (scrypt, SHA-256)"]
        DBEngine["SQLAlchemy 2 Engine"]
    end

    subgraph Database ["PostgreSQL (Port 5432)"]
        UsersTable[("users table")]
        SessionsTable[("sessions table")]
        StudentProfilesTable[("student_profiles table")]
        OrgProfilesTable[("organization_profiles table")]
        CoursesTable[("courses table")]
        EnrollmentsTable[("enrollments table")]
    end

    SPA -->|"Requests"| Proxy
    Proxy -->|"HTTP Forward"| AuthRouter & StudentRouter & OrgRouter & CourseRouter & EnrollmentRouter
    AuthRouter --> AuthService
    StudentRouter --> StudentService
    OrgRouter --> OrgService
    CourseRouter --> CourseService
    EnrollmentRouter --> EnrollmentService
    AuthService & StudentService & OrgService & CourseService & EnrollmentService --> DBEngine
    DBEngine --> UsersTable & SessionsTable & StudentProfilesTable & OrgProfilesTable & CoursesTable & EnrollmentsTable
    AuthRouter -->|"Set-Cookie: session_token"| CookieStorage
    CookieStorage -.->|"Automatic Cookie Transmission"| Deps
    Deps -->|"Resolve session"| AuthService
```

---

## 2. Component Boundaries

### 1. Backend Layer (`backend/app/`)
- **Core (`core/`)**:
  - `config.py`: Environment settings via `pydantic-settings`.
  - `database.py`: SQLAlchemy 2 engine with connection pooling and `get_db()` dependency.
  - `security.py`: Password hashing with stdlib `hashlib.scrypt` and SHA-256 session token hashing.
  - `deps.py`: `get_current_user` and `require_roles(*roles)` enforcing role authorization.
  - `exceptions.py`: Application exceptions mapped to standard HTTP status codes (`NotFoundException`, `ConflictException`, `ForbiddenException`, `UnauthorizedException`).
- **Models (`models/`)**:
  - `user.py`: `User` account model with `UserRole` enum (`student`, `instructor`, `organization`, `admin`).
  - `session.py`: `Session` model with user FK and indexed `token_hash`.
  - `student_profile.py`: `StudentProfile` model with 1-to-1 cascade FK to users.
  - `organization_profile.py`: `OrganizationProfile` model with 1-to-1 cascade FK to users.
  - `course.py`: `Course` model with `CourseStatus` enum (`draft`, `published`), instructor FK, title, description, timestamps.
  - `enrollment.py`: `Enrollment` model linking course and student with unique constraint.
  - `base.py`: Central `DeclarativeBase` metadata class.
- **Schemas (`schemas/`)**:
  - `auth.py`: `RegisterRequest`, `LoginRequest`, `UserResponse`.
  - `student_profile.py`: `StudentProfileUpdateRequest`, `StudentProfileResponse`.
  - `organization_profile.py`: `OrganizationProfileUpdateRequest`, `OrganizationProfileResponse`.
  - `course.py`: `CourseCreate` (extra="forbid"), `CourseUpdate` (extra="forbid"), `CourseResponse`, `CourseListResponse`.
  - `enrollment.py`: `EnrolledStudentResponse`, `EnrollmentResponse`, `EnrollmentActionResponse`.
  - `health.py`: Health verification schemas.
- **Routers (`routers/`)**:
  - Thin FastAPI HTTP endpoints under `/api`.
  - `auth.py`: `/register`, `/login`, `/logout`, `/me`.
  - `student_profile.py`: `/students/me`.
  - `organization_profile.py`: `/organizations/me`.
  - `course.py`: `/courses`, `/courses/{id}`, `/instructors/me/courses`, `/students/me/courses`.
  - `enrollment.py`: `/courses/{id}/enrollment`, `/courses/{id}/students`.
- **Services (`services/`)**:
  - `AuthService`: Registration (atomic user + profile), authentication, session lifecycle.
  - `StudentProfileService`: Student profile retrieval and updates.
  - `OrganizationProfileService`: Organization profile retrieval and updates.
  - `course.py`: Course creation, search and pagination, detail lookup with draft visibility guard, update with draft-reversion lock.
  - `enrollment.py`: Course enrollment with duplicate prevention, unenrollment, and roster retrieval.

### 2. Frontend Layer (`frontend/src/`)
- **API (`api/`)**:
  - `auth.ts`, `profile.ts`, `course.ts`, `health.ts`.
- **Context &amp; Navigation (`context/`, `config/`)**:
  - `AuthContext`: Session lifecycle and user identity.
  - `navigation.ts`: Navigation items filtered per role, role-based `getHomePath`.
- **Components (`components/`)**:
  - `components/courses/`: `CourseForm`, `CourseTable`, `EnrollButton`, `StudentRosterTable`.
  - `components/ui/`: `Button`, `TextField`, `Textarea`, `Select`, `Badge`, `DataTable`, `EmptyState`, `ErrorMessage`, `Notice`, `PageHeader`.
  - `components/layout/`: `AppShell`.
  - `components/routes/`: `ProtectedRoute`, `RoleRoute`.
- **Pages (`pages/`)**:
  - `/courses`: Course catalogue with title search, pagination, and admin status badges.
  - `/my-courses`: Role-specific view (student enrolled courses; instructor courses with "New course" button).
  - `/courses/new`: Instructor course creation form.
  - `/courses/:id/edit`: Instructor/admin course editing form.
  - `/courses/:id`: Course detail view with student enroll/leave button, owner publishing, and student roster table.
  - `/profile`: Role-specific student and organization profile views.
  - `/account`: Account details and credentials overview.
  - `/status`: Admin system status view.

---

## 3. Endpoints Matrix

| Endpoint | Method | Role Access | Description | Success Code |
| :--- | :--- | :--- | :--- | :--- |
| `/api/auth/register` | `POST` | Public | Register student or organization (atomic profile creation) | `201 Created` |
| `/api/auth/login` | `POST` | Public | Authenticate credentials &amp; start session | `200 OK` |
| `/api/auth/logout` | `POST` | Public | Terminate session &amp; clear cookie | `200 OK` |
| `/api/auth/me` | `GET` | Authenticated | Retrieve current user profile | `200 OK` |
| `/api/students/me` | `GET` | `student` | Retrieve authenticated student profile | `200 OK` |
| `/api/students/me` | `PUT` | `student` | Update authenticated student profile | `200 OK` |
| `/api/organizations/me` | `GET` | `organization` | Retrieve authenticated organization profile | `200 OK` |
| `/api/organizations/me` | `PUT` | `organization` | Update authenticated organization profile | `200 OK` |
| `/api/courses` | `POST` | `instructor` | Create course owned by authenticated instructor | `201 Created` |
| `/api/courses` | `GET` | Authenticated | List published courses (or all for admin) with ?q= and pagination | `200 OK` |
| `/api/courses/{id}` | `GET` | Authenticated | Get course details (visible if published, owned, or admin) | `200 OK` |
| `/api/courses/{id}` | `PATCH` | `instructor` (owner), `admin` | Update course title, description, or publish | `200 OK` |
| `/api/instructors/me/courses` | `GET` | `instructor` | Get instructor's own courses with enrolled count | `200 OK` |
| `/api/students/me/courses` | `GET` | `student` | Get student's enrolled courses | `200 OK` |
| `/api/courses/{id}/students` | `GET` | `instructor` (owner), `admin` | Get enrolled student roster with names and emails | `200 OK` |
| `/api/courses/{id}/enrollment` | `POST` | `student` | Enroll student in published course | `201 Created` |
| `/api/courses/{id}/enrollment` | `DELETE` | `student` | Unenroll student from course | `200 OK` |
| `/api/health` | `GET` | Public | Basic platform status probe | `200 OK` |
| `/api/health/db` | `GET` | Public | Database query connectivity probe | `200 OK` |
