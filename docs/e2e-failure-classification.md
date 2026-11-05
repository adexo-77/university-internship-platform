# E2E Test Suite Failure Classification & Root Cause Analysis

This document records the reproduction and classification of failures observed during full Playwright test runs across 5 viewports against the Docker development stack.

---

## Failure Matrix

| Failure Symptom | Observed Context | Root Cause | Classification | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| `page.waitForURL` timeout in `loginAs` on `tablet-768` and `desktop-1440` (~80 tests) | Full suite run across 5 viewports | Every test logged in via UI form (`/login`), generating ~240 login requests. The 101st request exceeded `RATE_LIMIT_LOGIN_IP_LIMIT` (100) returning HTTP 429, stalling navigation. | **Test-Harness Problem** | Implement `auth.setup.ts` with Playwright `storageState` to log in once per role (5 logins total) and reuse cookies. |
| `#apply-cover-letter` not found in `functional-student.spec.ts` | Second viewport project (`mobile-390`) after `mobile-360` | Test 3 applied and withdrew an application for "Data Analysis Intern". The second project ran against the same DB where the student already had a withdrawn application. | **Test-Harness Problem** (state mutation across viewports) + **App Policy** | Isolate destructive flows to `desktop-1440` with data reset; add explicit UI messaging that withdrawal is final. |
| `page.getByText('100 / 100')` failure in graded assignment test | Viewport projects in student flows | Strict-mode locator collision between the submission status badge and the assignment points summary. Additionally, leaving the course temporarily orphaned access. | **Test-Harness Problem** (strict locator collision) + **Real App Defect** | Use `.first()` on locator; implement service-layer guard preventing course leave when graded work exists. |
| User password change or user deactivation mutating test state | Multi-project runs against single DB | Password updates or admin deactivations altered user credentials for subsequent test specs. | **Test-Harness Problem** | Restrict state-modifying functional tests to single project with automated demo reseed between suites. |

---

## Detailed Defect Analysis

### 1. Rate Limit Exhaustion (`loginAs` at `page.waitForURL`)
- **Mechanism**: The original test architecture called `loginAs(page, DEMO_USERS[role])` in `beforeEach` for almost all ~49 tests across 5 browser projects (totaling ~245 login attempts).
- **Trigger**: Docker E2E stack sets `RATE_LIMIT_LOGIN_IP_LIMIT=100`. At test #101 (during `tablet-768`), the backend returned `429 Too Many Requests`. The UI showed an error banner instead of redirecting, causing `page.waitForURL` to time out after 15s.
- **Remedy**: Playwright authentication setup (`auth.setup.ts`) generates `.auth/<role>.json` session cookies once per role (5 total logins). All subsequent test projects load authenticated storage state instantly with zero HTTP login overhead.

### 2. Cross-Viewport Data Pollution
- **Mechanism**: Functional tests perform state mutations: enrolling/leaving courses, submitting assignments, and submitting/withdrawing internship applications.
- **Trigger**: Running functional suites on 5 separate viewports in parallel or sequence against a single PostgreSQL database causes subsequent viewports to encounter mutated states. For instance, once an application is withdrawn, the application form (`#apply-cover-letter`) is replaced with the withdrawn status panel.
- **Remedy**: Non-destructive crawlers and layout tests run on all 5 viewports. Destructive functional flows run exclusively on `desktop-1440` with automated demo database reseeding before execution.

### 3. Academic Integrity Guard: Course Leave with Graded Work
- **Mechanism**: Previously, `leave_course` deleted the `Enrollment` record regardless of whether student work had been submitted and evaluated.
- **Defect**: While submissions remained in the database, the student disappeared from the course roster and instructor grading views, orphaning assigned grades and compromising academic audit trails.
- **Remedy**: `leave_course` must verify that no submissions for the course have received a grade. If graded submissions exist, the action is rejected with `409 Conflict` (`GRADED_WORK_EXISTS`), and the UI disables the leave affordance with explanatory messaging.

---

## Resolved Test Architecture &amp; Execution

- **Authentication Caching**: An initial `setup` project logs in once per role and persists session storage in `e2e/.auth/<role>.json`. Tests import these storage states directly via `authenticateAsRole`, reducing HTTP authentication requests to 5 setup sessions and avoiding rate-limiting or lockout issues.
- **Separation of Concerns**: Non-destructive crawlers, accessibility scans (axe-core), responsive checks, and error paths run across all 5 device viewports (`mobile-360`, `mobile-390`, `tablet-768`, `desktop-1440`, `desktop-1920`). Mutating functional flows are grouped in `frontend/e2e/flows/` and execute sequentially in a dedicated desktop project (`desktop-1440`).
- **Automated Demo Reset**: A setup hook invokes `scripts/seed_demo.py --reset-demo` prior to running the functional flows, ensuring tests are deterministic and isolated.
- **Execution Commands**:
  - `npm run test:e2e`: Runs complete suite under 10 minutes.
  - `npm run test:e2e:fast`: Runs non-destructive viewports only (~4-5 minutes).
  - `npm run test:e2e:flows`: Runs functional flows with automated demo reset (~1-2 minutes).
