# Database Architecture &bull; Entity Relationship Specification

This document details the PostgreSQL schema managed via SQLAlchemy 2 declarative models and Alembic migrations.

---

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    users ||--o{ sessions : "has active sessions"
    users ||--o| student_profiles : "has profile (student)"
    users ||--o| organization_profiles : "has profile (organization)"
    users ||--o{ courses : "instructs (instructor)"
    users ||--o{ enrollments : "enrolled in (student)"
    users ||--o{ submissions : "submits coursework (student)"
    courses ||--o{ enrollments : "has enrollments"
    courses ||--o{ assignments : "has assignments"
    assignments ||--o{ submissions : "has submissions"

    users {
        int id PK "autoincrement"
        string email UK "lowercase, indexed, max 255"
        string password_hash "scrypt hash with salt"
        string full_name "max 255"
        user_role role "enum: student | instructor | organization | admin"
        boolean is_active "default true"
        timestamp created_at "with time zone, server default now()"
        timestamp updated_at "with time zone, server default now(), on update"
    }

    sessions {
        int id PK "autoincrement"
        int user_id FK "users.id, ON DELETE CASCADE, indexed"
        string token_hash UK "SHA-256 hex, indexed, 64 chars"
        timestamp created_at "with time zone, server default now()"
        timestamp expires_at "with time zone, indexed"
    }

    student_profiles {
        int id PK "autoincrement"
        int user_id FK "users.id, ON DELETE CASCADE, unique, indexed"
        string university "nullable, max 255"
        string department "nullable, max 255"
        int year_of_study "nullable, check: 1 <= year <= 6"
        string bio "nullable, max 1000"
        string_array skills "text array, default empty, max 20 items"
        timestamp updated_at "with time zone, server default now(), on update"
    }

    organization_profiles {
        int id PK "autoincrement"
        int user_id FK "users.id, ON DELETE CASCADE, unique, indexed"
        string organization_name "required, max 255"
        string industry "nullable, max 255"
        string location "nullable, max 255"
        string website "nullable, valid http/https URL, max 255"
        string description "nullable, max 1000"
        timestamp updated_at "with time zone, server default now(), on update"
    }

    courses {
        int id PK "autoincrement"
        int instructor_id FK "users.id, ON DELETE CASCADE, indexed"
        string title "max 120"
        string description "nullable, max 2000"
        course_status status "enum: draft | published, default draft"
        timestamp created_at "with time zone, server default now()"
        timestamp updated_at "with time zone, server default now(), on update"
    }

    enrollments {
        int id PK "autoincrement"
        int course_id FK "courses.id, ON DELETE CASCADE"
        int student_id FK "users.id, ON DELETE CASCADE, indexed"
        timestamp enrolled_at "with time zone, server default now()"
    }

    assignments {
        int id PK "autoincrement"
        int course_id FK "courses.id, ON DELETE CASCADE, indexed"
        string title "max 120"
        string description "nullable, max 2000"
        timestamp due_at "with time zone, required"
        int max_points "default 100, 1-1000"
        timestamp created_at "with time zone, server default now()"
        timestamp updated_at "with time zone, server default now(), on update"
    }

    submissions {
        int id PK "autoincrement"
        int assignment_id FK "assignments.id, ON DELETE CASCADE, indexed"
        int student_id FK "users.id, ON DELETE CASCADE, indexed"
        string content "text, 1-10000 chars"
        string link_url "nullable, valid http/https, max 2048"
        boolean is_late "default false"
        timestamp submitted_at "with time zone, server default now()"
        timestamp updated_at "with time zone, server default now(), on update"
        int grade "nullable, 0 to max_points"
        string feedback "nullable, max 2000"
        timestamp graded_at "nullable, with time zone"
        int graded_by FK "users.id, ON DELETE SET NULL, nullable"
    }
```

---

## 2. Table Specifications

### `users`

Represents all registered accounts across all roles in the platform.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier for user account |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE`, `INDEX` | Normalized lowercase email address |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | `hashlib.scrypt` hash with unique random salt |
| `full_name` | `VARCHAR(255)` | `NOT NULL` | Display and legal name of the user |
| `role` | `user_role` | `NOT NULL` | PostgreSQL native enum (`student`, `instructor`, `organization`, `admin`) |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT TRUE` | Account active state for suspension / activation |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Account creation timestamp in UTC |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Last update timestamp in UTC |

### `sessions`

Represents active authentication sessions backed by HttpOnly cookies.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique session record identifier |
| `user_id` | `INTEGER` | `NOT NULL`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Owning account reference |
| `token_hash` | `VARCHAR(64)` | `NOT NULL`, `UNIQUE`, `INDEX` | SHA-256 hex digest of the raw session token |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Session inception timestamp in UTC |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL`, `INDEX` | Session expiry timestamp in UTC (default 7 days) |

### `student_profiles`

Represents optional academic background and skills profile for student accounts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique profile identifier |
| `user_id` | `INTEGER` | `NOT NULL`, `UNIQUE`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Owning student user account |
| `university` | `VARCHAR(255)` | `NULLABLE` | Attending university or institution |
| `department` | `VARCHAR(255)` | `NULLABLE` | Faculty or academic department |
| `year_of_study` | `INTEGER` | `NULLABLE`, `CHECK (1 <= year_of_study <= 6)` | Academic progress year (1 to 6) |
| `bio` | `VARCHAR(1000)` | `NULLABLE` | Student background and career interests |
| `skills` | `VARCHAR(40)[]` | `NOT NULL`, `DEFAULT '{}'` | Array of up to 20 skill tags |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Profile last modification timestamp |

### `organization_profiles`

Represents company details, industry sector, and contact points for organization accounts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique profile identifier |
| `user_id` | `INTEGER` | `NOT NULL`, `UNIQUE`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Owning organization user account |
| `organization_name` | `VARCHAR(255)` | `NOT NULL` | Required name of the organization |
| `industry` | `VARCHAR(255)` | `NULLABLE` | Operating industry or business vertical |
| `location` | `VARCHAR(255)` | `NULLABLE` | Office city, country, or location |
| `website` | `VARCHAR(255)` | `NULLABLE` | Valid HTTP or HTTPS web URL |
| `description` | `VARCHAR(1000)` | `NULLABLE` | Organization mission, culture, and overview |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Profile last modification timestamp |

### `courses`

Represents instructor-created learning courses with draft/published lifecycle.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique course identifier |
| `instructor_id` | `INTEGER` | `NOT NULL`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Owning instructor user account |
| `title` | `VARCHAR(120)` | `NOT NULL` | Course title (3 to 120 characters) |
| `description` | `VARCHAR(2000)` | `NULLABLE` | Syllabus and course outline |
| `status` | `course_status` | `NOT NULL`, `DEFAULT 'draft'` | Enum status (`draft`, `published`) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Creation timestamp in UTC |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Last update timestamp in UTC |

### `enrollments`

Represents student enrollment linking a student account to a course.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique enrollment identifier |
| `course_id` | `INTEGER` | `NOT NULL`, `FK courses(id) ON DELETE CASCADE` | Course reference |
| `student_id` | `INTEGER` | `NOT NULL`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Enrolled student user reference |
| `enrolled_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Enrollment timestamp in UTC |
| &mdash; | &mdash; | `UNIQUE (course_id, student_id)` | Prevents duplicate student enrollments |

### `assignments`

Represents coursework, problem sets, and practical assignments created by instructors.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique assignment identifier |
| `course_id` | `INTEGER` | `NOT NULL`, `FK courses(id) ON DELETE CASCADE`, `INDEX` | Owning course reference |
| `title` | `VARCHAR(120)` | `NOT NULL` | Assignment title (3 to 120 characters) |
| `description` | `TEXT` | `NULLABLE` | Assignment instructions and rubric (up to 2000 chars) |
| `due_at` | `TIMESTAMPTZ` | `NOT NULL` | Timezone-aware due deadline (must be in future on creation) |
| `max_points` | `INTEGER` | `NOT NULL`, `DEFAULT 100`, `1 <= points <= 1000` | Maximum points achievable |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Creation timestamp in UTC |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Last update timestamp in UTC |

### `submissions`

Represents student work submitted for an assignment, along with grades and instructor feedback.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique submission identifier |
| `assignment_id` | `INTEGER` | `NOT NULL`, `FK assignments(id) ON DELETE CASCADE`, `INDEX` | Assignment reference |
| `student_id` | `INTEGER` | `NOT NULL`, `FK users(id) ON DELETE CASCADE`, `INDEX` | Enrolled student reference |
| `content` | `TEXT` | `NOT NULL` | Student written response (1 to 10000 characters) |
| `link_url` | `VARCHAR(2048)` | `NULLABLE` | Optional artifact URL (must use http or https) |
| `is_late` | `BOOLEAN` | `NOT NULL`, `DEFAULT FALSE` | Computed from server clock at submission time |
| `submitted_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Initial submission timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` | Last modification timestamp |
| `grade` | `INTEGER` | `NULLABLE`, `0 <= grade <= max_points` | Awarded grade score |
| `feedback` | `VARCHAR(2000)` | `NULLABLE` | Instructor feedback comments (up to 2000 characters) |
| `graded_at` | `TIMESTAMPTZ` | `NULLABLE` | Grading timestamp in UTC |
| `graded_by` | `INTEGER` | `NULLABLE`, `FK users(id) ON DELETE SET NULL` | Instructor user who graded the work |
| &mdash; | &mdash; | `UNIQUE (assignment_id, student_id)` | One submission record per student per assignment |

---

## 3. Security &amp; Data Integrity Rules

1. **Token Storage**: Raw session tokens are never stored in the database. Only the SHA-256 digest is persisted in `sessions.token_hash`.
2. **Credential Privacy**: `password_hash` is never included in API responses or logs.
3. **Cascade Invalidation**: Deleting a user account cascades to automatically drop all active sessions, associated profile records (`student_profiles` or `organization_profiles`), created courses (for instructors), enrollments (for students), and submissions.
4. **Stale Session Purging**: Expired sessions are checked against `expires_at` and automatically deleted upon access resolution.
5. **Atomic Registration Transaction**: User creation and initial profile creation occur in the same database transaction; failure of either rolls back both.
6. **Session-Bound Identity**: Endpoints resolving profiles, creating courses, or enrolling students derive user identity solely from the verified session, never allowing external modification or spoofing of foreign keys.
7. **One-Way Status Transition**: Courses can transition from `draft` to `published`, but published courses cannot be reverted to `draft` (enforced with 409 Conflict).
8. **Unique Enrollment**: Unique constraint on `(course_id, student_id)` prevents double-enrollment, backed by 409 Conflict handling.
9. **Future Due Date on Assignment Creation**: Assignments must have a timezone-aware `due_at` date set in the future upon creation (enforced with 422 / 409 validation).
10. **Grade Floor on Max Points Modification**: An assignment's `max_points` cannot be decreased below any already-awarded student grade (enforced with 409 Conflict).
11. **Protected Assignment Deletion**: An assignment cannot be deleted if student submissions have been recorded (enforced with 409 Conflict).
12. **Submission Lock Upon Grading**: Once a submission receives a grade and `graded_at` timestamp, further student edits or resubmissions are rejected with 409 Conflict.
13. **Instructor-Only Grading**: Only the course owner instructor can grade or regrade student work; administrators possess read-only access (403 Forbidden).
