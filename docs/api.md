# REST API Reference &bull; University Learning &amp; Internship Platform

The **University Learning &amp; Internship Platform** provides a modern, fully typed REST API built with **FastAPI** and **Pydantic v2**. This document describes the API architecture, authentication model, endpoint contracts, error envelopes, and automated OpenAPI schema export workflows.

---

## 1. Overview &amp; Interactive Documentation

- **Base URL**: `http://localhost:8001/api`
- **Interactive Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc UI**: [http://localhost:8001/redoc](http://localhost:8001/redoc)
- **OpenAPI 3.1 Schema**: Stored in version control at [`docs/openapi.json`](openapi.json)

### Generating &amp; Verifying OpenAPI Schema
The OpenAPI contract is kept strictly in sync with the FastAPI routes via `scripts/export_openapi.py`:

```powershell
# Export latest OpenAPI schema to docs/openapi.json
python scripts/export_openapi.py

# Verify schema synchronization via Pytest
python -m pytest backend/tests/test_openapi_export.py -v
```

---

## 2. Authentication &amp; Session Management

Authentication uses stateful, server-managed sessions with cryptographically random tokens:
- **Cookie Name**: `session_id`
- **Security Flags**: `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure` (in production)
- **Session Expiry**: Configurable TTL (default 24 hours); expired sessions are automatically purged.
- **Identity Decoupling**: Identity is resolved exclusively from the server session record in PostgreSQL. The server rejects any client attempts to forge user identities through headers or request bodies.

---

## 3. Endpoints Matrix

### Health Check Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Public | Application liveness probe returning system status, timestamp, and environment. |
| `GET` | `/api/health/db` | Public | Database readiness probe verifying active PostgreSQL connection pooling. |

### Authentication &amp; Account Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register a new user account (`student` or `organization`). |
| `POST` | `/api/auth/login` | Public | Authenticate credentials, create session, and set `session_id` cookie. |
| `POST` | `/api/auth/logout` | Authenticated | Destroy current session record in PostgreSQL and expire cookie. |
| `GET` | `/api/auth/me` | Authenticated | Retrieve authenticated user profile and active role permissions. |
| `POST` | `/api/auth/change-password` | Authenticated | Change user password with current password verification. |

### User Profile Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students/me` | Student | Retrieve student bio, university, department, year, skills, and profile completion status. |
| `PUT` | `/api/students/me` | Student | Update student profile attributes (university, department, year, bio, skills). |
| `GET` | `/api/organizations/me` | Organization | Retrieve corporate profile, industry, size, website, and approval status. |
| `PUT` | `/api/organizations/me` | Organization | Update organization profile attributes. |

### Course Management Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/courses` | Authenticated | Browse published courses or filter by instructor ownership. |
| `POST` | `/api/courses` | Instructor | Author a new course (`draft` or `published`). |
| `GET` | `/api/courses/{id}` | Authenticated | Retrieve detailed course view, syllabus outline, and instructor info. |
| `PATCH` | `/api/courses/{id}` | Course Instructor, Admin | Update course details, syllabus, or lifecycle state (`draft`, `published`, `archived`). |
| `GET` | `/api/courses/{id}/students` | Course Instructor, Admin | Inspect enrolled student roster with enrollment timestamps. |

### Course Enrollment Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/courses/{id}/enrollment` | Student | Enroll in an active, published course (duplicate guarded). |
| `DELETE` | `/api/courses/{id}/enrollment` | Student | Unenroll from a course. |

### Course Learning Resource Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/courses/{id}/resources` | Instructor (Owner), Admin, Enrolled Student | List curated external learning resources for course (enrolled only if published). |
| `POST` | `/api/courses/{id}/resources` | Course Instructor (Owner) | Add learning resource link (up to 50 per course, http/https). |
| `PATCH` | `/api/resources/{id}` | Course Instructor (Owner) | Update learning resource title, URL, or description. |
| `DELETE` | `/api/resources/{id}` | Course Instructor (Owner) | Delete course learning resource. |

### Assignment &amp; Submission Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/courses/{id}/assignments` | Authenticated | List all assignments defined for a specific course (with submission state). |
| `POST` | `/api/courses/{id}/assignments` | Course Instructor | Create an assignment with due date and maximum points. |
| `GET` | `/api/assignments/{id}` | Authenticated | Retrieve assignment prompt, deadline, and scoring details. |
| `PATCH` | `/api/assignments/{id}` | Course Instructor | Update assignment parameters (max_points floor checked). |
| `DELETE` | `/api/assignments/{id}` | Course Instructor | Delete assignment (protected against active submissions). |
| `GET` | `/api/assignments/{id}/submissions` | Course Instructor, Admin | View submission roster for an assignment. |
| `PUT` | `/api/assignments/{id}/submission` | Enrolled Student | Submit or update coursework; automatically tags `is_late=true` if past due. |
| `GET` | `/api/assignments/{id}/submission` | Enrolled Student | Retrieve student's own submission and grading status. |
| `PUT` | `/api/submissions/{id}/grade` | Course Instructor | Assign numeric score (0 to max) and qualitative instructor feedback. |

### Internship Postings &amp; Application Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/internships` | Student, Admin | Search published listings with work mode and keyword filters. |
| `POST` | `/api/internships` | Approved Org | Create a new internship posting (`draft` or `pending_review`). |
| `GET` | `/api/internships/{id}` | Authenticated | View internship posting details and application status. |
| `PATCH` | `/api/internships/{id}` | Posting Org | Update posting details or extend deadline up to 90 days. |
| `POST` | `/api/internships/{id}/submit` | Posting Org | Submit draft posting for admin review (requires approved org). |
| `POST` | `/api/internships/{id}/withdraw` | Posting Org | Withdraw pending_review posting back to draft. |
| `POST` | `/api/internships/{id}/close` | Posting Org | Close open internship posting. |
| `GET` | `/api/internships/{id}/applications` | Posting Org, Admin | Review student applications and cover letters for a posting. |
| `POST` | `/api/internships/{id}/applications` | Student | Apply with personalized cover letter (requires profile with university &amp; department). |
| `GET` | `/api/students/me/applications` | Student | List all applications submitted by the current student. |
| `POST` | `/api/applications/{id}/withdraw` | Student | Withdraw a pending application before final hiring decision. |
| `PUT` | `/api/applications/{id}/decision` | Posting Org | Advance candidate status (`shortlisted`, `accepted`, `rejected`). |

### Administration Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/admin/users` | Admin | Search and filter platform user accounts by role and status. |
| `POST` | `/api/admin/users` | Admin | Provision instructor or administrator account. |
| `PATCH` | `/api/admin/users/{id}` | Admin | Activate or deactivate account (self-deactivation guarded). |
| `PUT` | `/api/admin/users/{id}/password` | Admin | Administratively reset user password and invalidate active sessions. |
| `GET` | `/api/admin/organizations` | Admin | Review pending organization registrations. |
| `PUT` | `/api/admin/organizations/{user_id}/approval` | Admin | Approve, reject, or reset company registration status with note. |
| `GET` | `/api/admin/internships` | Admin | Moderation queue for submitted internship postings. |
| `PUT` | `/api/admin/internships/{id}/review` | Admin | Approve, reject, or take down listing with review note. |

### Notification Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/notifications` | Authenticated | Retrieve paginated notifications list for current user (?limit=, ?offset=). |
| `GET` | `/api/notifications/unread-count` | Authenticated | Retrieve unread notifications count for navigation badge. |
| `PATCH` | `/api/notifications/{id}/read` | Authenticated | Mark single notification owned by current user as read. |
| `POST` | `/api/notifications/read-all` | Authenticated | Mark all notifications owned by current user as read. |

### Role Dashboard Endpoints
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard/student` | Student | Enrolled courses, assignments due soon, recent grades, and application metrics. |
| `GET` | `/api/dashboard/instructor` | Instructor | Active courses, student count, and "Needs Grading" queue. |
| `GET` | `/api/dashboard/organization` | Organization | Active postings, pending reviews, and candidate pipeline totals. |
| `GET` | `/api/dashboard/admin` | Admin | Platform-wide user metrics, pending reviews, and status breakdowns. |

---

## 4. Standard Response &amp; Error Format

All error responses return consistent JSON envelopes:

```json
{
  "detail": "Descriptive human-readable error message.",
  "code": "MACHINE_READABLE_ERROR_CODE",
  "request_id": "optional-traceability-uuid"
}
```

### Common HTTP Status Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Validation failure or illegal domain operation.
- `401 Unauthorized`: Missing or invalid session cookie.
- `403 Forbidden`: Authenticated user lacks required role or resource ownership.
- `404 Not Found`: Target resource does not exist.
- `409 Conflict`: Unique constraint violation (e.g., duplicate enrollment).
- `422 Unprocessable Entity`: Request body failed Pydantic schema validation.
- `429 Too Many Requests`: Rate limit exceeded; client must wait `Retry-After` seconds.
- `500 Internal Server Error`: Unhandled exception (sanitized, stack trace hidden).
- `503 Service Unavailable`: Database connectivity interrupted.
