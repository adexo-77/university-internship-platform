# End-User Guide &bull; University Learning &amp; Internship Platform

This guide provides step-by-step instructions for evaluating and operating the platform across each user role (**Student**, **Instructor**, **Organization**, and **Administrator**). All scenarios are designed to work seamlessly with the pre-seeded demo dataset.

---

## 1. Getting Started &amp; Authentication

### Running the Services
Ensure both backend and frontend development servers are running:
- **Backend API**: `http://localhost:8001` (FastAPI with OpenAPI docs at `/docs`)
- **Frontend SPA**: `http://localhost:5173` (Vite + React)

### Logging In
1. Navigate to [http://localhost:5173/login](http://localhost:5173/login).
2. Enter the email corresponding to the role you wish to test.
3. Enter the standard demo password configured in `.env` (`DEMO_USER_PASSWORD`, defaults to `DemoPassword123!`).
4. Click **Sign in**. The application will authenticate your session and route you directly to your role-specific dashboard.

---

## 2. Student Role Guide

### Demo Accounts
- **Ready Student**: `demo.student@example.com` (complete profile, enrolled courses, existing submissions)
- **New Student**: `demo.student2@example.com` (incomplete profile demonstrating prerequisite guards)

### Step 1: Explore the Student Dashboard (`/`)
1. Log in as `demo.student@example.com`.
2. Notice the top stat strip displaying:
   - **Enrolled Courses** total.
   - **Pending Assignments** count.
   - **Active Applications** in your career pipeline.
3. Review the **Assignments Due Soon** panel:
   - Assignments due within 72 hours show an amber/red **Urgent** badge.
   - Assignments with future deadlines display an **Upcoming** badge.
   - Assignments past deadline display a **Past Due** badge.
4. Review the **Recent Grades** panel showing scored assignments with percentage chips and instructor feedback.

### Step 2: Browse &amp; Enroll in Courses (`/courses`)
1. Click **Courses** in the main navigation.
2. Use the search bar to filter by course title, code (e.g., `CS101`), or department.
3. Click on a course card to view the **Course Details** page.
4. Review the syllabus outline, instructor information, and assignment list.
5. Click **Enroll** to join a course (or **Leave Course** to unenroll). Duplicate enrollments are prevented by backend database constraints.

### Step 3: Complete &amp; Submit Assignments (`/assignments/:id`)
1. From a course detail page or your dashboard, click an assignment title.
2. Read the assignment instructions, deadline timestamp, and maximum score.
3. If you have not submitted yet, enter your response in the **Submission Text** area and click **Submit Assignment**.
4. If submitting after the deadline, notice that the submission is accepted but automatically tagged with a red **Late** badge.
5. Once the instructor grades your submission, notice that your score and comments appear, and further edits are strictly locked.

### Step 4: Manage Profile &amp; Test Prerequisite Guard (`/profile`)
1. Click your name in the top navigation and select **Profile**.
2. Update your bio and add technical skill tags (e.g., `Python`, `React`, `SQL`), then click **Save Profile**.
3. **Guard Test**: Log in as `demo.student2@example.com`. Notice the warning banner stating your profile is incomplete. Navigate to `/internships`, select an internship, and observe that the **Apply** button warns you to complete your profile before applying.

### Step 5: Search &amp; Apply for Internships (`/internships`)
1. Log in as `demo.student@example.com`.
2. Navigate to **Internships** to browse vetted opportunities.
3. Filter by work mode: **Remote**, **Hybrid**, or **On-site**.
4. Select an active listing and click **Apply**.
5. Fill in your personalized cover letter and submit your application.
6. Navigate to **My Applications** (`/my-applications`) to monitor review statuses (`submitted`, `shortlisted`, `accepted`, `rejected`).
7. To withdraw an application before a hiring decision is finalized, click **Withdraw** and confirm the prompt.

---

## 3. Instructor Role Guide

### Demo Account
- **Instructor**: `demo.instructor@example.com`

### Step 1: Review the Instructor Dashboard (`/`)
1. Log in as `demo.instructor@example.com`.
2. The dashboard highlights:
   - **Active Courses** published.
   - **Total Enrolled Students** across all courses.
   - **Needs Grading** count of student submissions awaiting evaluation.
3. Click any submission in the "Needs Grading" list to jump directly to the grading interface.

### Step 2: Create &amp; Manage Courses (`/courses/new`)
1. Click **Courses** &rarr; **Create Course** (or access via the dashboard quick action).
2. Enter the course code (e.g., `CS301`), title, department, and comprehensive syllabus text.
3. Choose the initial status: `draft` (hidden from students) or `published` (visible in catalog).
4. Save the course. On the course detail page, view the **Enrolled Students Roster** showing enrolled student names, emails, and enrollment dates.

### Step 3: Create Course Assignments (`/courses/:id`)
1. On your course detail page, click **New Assignment**.
2. Enter the assignment title, detailed prompt instructions, due date, and maximum possible points (e.g., `100`).
3. Click **Create Assignment**. The assignment becomes immediately available to all enrolled students.

### Step 4: Grade Student Submissions (`/submissions/:id/grade`)
1. Open the course assignment and scroll to the **Submissions Roster**.
2. Submissions awaiting review display a yellow **Pending Review** badge.
3. Click **Grade** next to a student submission.
4. Enter a numeric grade (enforced between `0` and `max_score`) and enter constructive instructor feedback.
5. Click **Submit Grade**. The submission status transitions to `graded`, and the student's dashboard updates immediately.

---

## 4. Organization Role Guide

### Demo Accounts
- **Approved Organization**: `demo.org@example.com` (vetted company with live postings)
- **Pending Organization**: `demo.neworg@example.com` (new registrant awaiting admin verification)

### Step 1: Review the Organization Dashboard (`/`)
1. Log in as `demo.org@example.com`.
2. Review company metrics:
   - **Active Listings** currently accepting applications.
   - **Pending Review** postings in the moderation queue.
   - **Total Applications** received across all postings.

### Step 2: Manage Company Profile (`/profile`)
1. Navigate to **Profile** to update company information:
   - Organization Name
   - Industry category (e.g., `FinTech`, `Healthcare`, `Software`)
   - Company Size (e.g., `51-200 employees`)
   - Official Website URL
2. Save changes to ensure student applicants see verified company details.

### Step 3: Post an Internship Listing (`/internships/new`)
1. Click **Post Internship**.
2. Fill in the job title, department, description, requirements, location, work mode (`remote`/`hybrid`/`onsite`), stipend amount, and application deadline.
3. Submit the listing.
   - Postings enter the `pending_review` state to allow platform administrators to verify the opportunity.
4. **Vetting Demonstration**: Log in as `demo.neworg@example.com`. Observe that posting creation is disabled with an explanatory banner informing the company that administrative approval is required first.

### Step 4: Candidate Pipeline &amp; Hiring Decisions (`/internships/:id`)
1. Navigate to **My Postings** (`/my-internships`) as `demo.org@example.com`.
2. Select a listing with applicants (e.g., *Frontend Engineering Intern*).
3. Review the **Applicants Roster** displaying applicant names, emails, skills, submission dates, and cover letters.
4. Click **Review Application** to advance a candidate through the hiring pipeline:
   - Click **Shortlist** to move a candidate into second-round review.
   - Click **Accept** to extend an internship offer.
   - Click **Reject** to decline an applicant.
5. Notice that terminal decisions (`accepted` or `rejected`) lock the application to prevent accidental state tampering.

---

## 5. Administrator Role Guide

### Demo Account
- **System Administrator**: `demo.admin@example.com`

### Step 1: Access the Administrator Dashboard (`/`)
1. Log in as `demo.admin@example.com`.
2. Inspect the high-level platform health indicators:
   - Total users across Student, Instructor, Organization, and Admin roles.
   - Pending Organization registrations requiring vetting.
   - Pending Internship postings requiring content moderation.

### Step 2: User Account Administration (`/admin/users`)
1. Click **Admin** &rarr; **Users** in the navigation bar.
2. Filter accounts by role or search by name and email.
3. **Deactivation / Activation**:
   - Click **Deactivate** on an active account to revoke platform access.
   - **Self-Protection Guard**: Notice that deactivation controls are disabled on your own account to prevent lockouts.
4. **Administrative Password Reset**:
   - Click **Reset Password** on any user row.
   - A modal generates a cryptographically secure temporary password and invalidates all existing active sessions for that account immediately.

### Step 3: Organization Vetting Queue (`/admin/organizations`)
1. Navigate to **Admin** &rarr; **Organizations**.
2. Find unverified companies (such as `demo.neworg@example.com` with status `pending_review`).
3. Click **Review**. Verify company details and website.
4. Click **Approve Organization** to grant full posting privileges, or **Reject** if the company cannot be verified.

### Step 4: Internship Content Moderation (`/admin/internships`)
1. Navigate to **Admin** &rarr; **Internship Reviews**.
2. Filter listings with status `pending_review`.
3. Open a pending submission:
   - Click **Approve** to publish the listing directly into the student search catalog.
   - Click **Reject** and provide a mandatory review note explaining what edits are required.
4. For active listings that violate institutional policies, administrators can issue an immediate **Takedown**, transitioning the status to `closed`.

---

## 6. Account Self-Service &amp; Session Management

### Changing Passwords (`/account`)
Any authenticated user can update their password:
1. Click your user avatar / email in the top navigation and select **Account Settings**.
2. Enter your current password and your new password (minimum 8 characters).
3. Upon submission, the server verifies the current hash, updates the Argon2id hash, and updates your session.

### Logging Out
1. Click **Sign out** in the navigation bar.
2. The server invalidates the session record in PostgreSQL and clears the `HttpOnly` cookie.
3. The browser is redirected to `/login`, and protected route access is immediately blocked.
