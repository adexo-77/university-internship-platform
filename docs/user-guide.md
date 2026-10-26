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
3. Enter the standard evaluation demo password: `12345678` (demo-only).
4. Click **Sign in**. The application will authenticate your session and route you directly to your role-specific dashboard.

---

## 2. Student Role Guide

### Demo Accounts
- **Ready Student**: Abel Tesfaye (`abel.tesfaye@example.com`, complete profile, enrolled courses, existing submissions)
- **Ready Student**: Meron Girma (`meron.girma@example.com`, complete profile, enrolled courses, late submission)
- **Incomplete Profile Student**: Dawit Lemma (`dawit.lemma@example.com`, incomplete profile demonstrating the profile-complete rule before applying)

### Step 1: Explore the Student Dashboard (`/`)
1. Log in as `abel.tesfaye@example.com`.
2. Notice the top stat strip displaying:
   - **Enrolled Courses** total (e.g., 2 courses).
   - **Pending Assignments** count.
   - **Active Applications** in your career pipeline.
3. Review the **Assignments Due Soon** panel:
   - "Relational Schema Design &amp; Normalization" due in 3 days displays an urgent badge.
   - "Advanced SQL Queries &amp; Index Optimization" due in 18 days displays an upcoming badge.
   - "ER Diagramming &amp; Conceptual Modeling" past due displays a past due badge.
4. Review the **Recent Grades** panel showing scored assignments with percentage chips and instructor feedback (e.g., 94% on ER Diagramming).

### Step 2: Browse &amp; Enroll in Courses (`/courses`)
1. Click **Courses** in the main navigation.
2. Use the search bar to filter by course title (e.g., "Database Systems"), code, or department.
3. Click on a course card to view the **Course Details** page.
4. Review the syllabus outline, instructor information (Dr. Tadesse Bekele), and assignment list.
5. Click **Enroll** to join a course (or **Leave Course** to unenroll). Duplicate enrollments are prevented by backend database constraints.

### Step 3: Complete &amp; Submit Assignments (`/assignments/:id`)
1. From a course detail page or your dashboard, click an assignment title.
2. Read the assignment instructions, deadline timestamp, and maximum score.
3. If submitting before the deadline, enter your response and project repository URL in the **Submission Text** area and click **Submit Assignment**.
4. Log in as `meron.girma@example.com` to observe a late submission tagged with a red **Late** badge.
5. Once the instructor grades your submission, notice that your score and comments appear, and further edits are strictly locked.

### Step 4: Manage Profile &amp; Test Profile-Complete Rule Before Applying (`/profile`)
1. Log in as `abel.tesfaye@example.com`. Click your name in the top navigation and select **Profile**.
2. Notice your profile attributes: Jimma University, Information Technology, Year 4, and technical skills tags (`Python`, `FastAPI`, `React`, `PostgreSQL`, `Docker`, `Git`).
3. **Profile-Complete Rule Test**: Log in as `dawit.lemma@example.com`. Notice the warning banner stating your profile is incomplete (missing university and department). Navigate to `/internships`, select an internship, and observe that submitting an application is blocked until your university and department profile fields are completed.

### Step 5: Search &amp; Apply for Internships (`/internships`)
1. Log in as `abel.tesfaye@example.com`.
2. Navigate to **Internships** to browse vetted opportunities (e.g., Junior Web Developer Intern at Kaffa Digital Solutions).
3. Filter by work mode: **Remote**, **Hybrid**, or **On-site**.
4. Select an active listing and click **Apply**.
5. Fill in your personalized cover letter and submit your application.
6. Navigate to **My Applications** (`/my-applications`) to monitor review statuses:
   - Junior Web Developer Intern: **Accepted**
   - Network Support Intern: **Rejected**
   - Systems Administration Intern 2025: **Withdrawn**

---

## 3. Instructor Role Guide

### Demo Accounts
- **Course Instructor**: Dr. Tadesse Bekele (`tadesse.bekele@example.com`)
- **Curriculum Instructor**: Ms. Hana Worku (`hana.worku@example.com`)

### Step 1: Review the Instructor Dashboard (`/`)
1. Log in as `tadesse.bekele@example.com`.
2. The dashboard highlights:
   - **Active Courses** published (Database Systems, Introduction to Programming).
   - **Total Enrolled Students** across all courses.
   - **Needs Grading** count of student submissions awaiting evaluation (Meron Girma's submission).
3. Click any submission in the "Needs Grading" list to jump directly to the grading interface.

### Step 2: Create &amp; Manage Courses (`/courses/new`)
1. Click **Courses** &rarr; **Create Course** (or access via the dashboard quick action).
2. Enter the course code (e.g., `IT302`), title, department, and comprehensive syllabus text.
3. Choose the initial status: `draft` (hidden from students) or `published` (visible in catalog).
4. Save the course. On the course detail page, view the **Enrolled Students Roster** showing enrolled student names, emails, and enrollment dates.

### Step 3: Create Course Assignments (`/courses/:id`)
1. On your course detail page, click **New Assignment**.
2. Enter the assignment title, detailed prompt instructions, due date, and maximum possible points (e.g., `100`).
3. Click **Create Assignment**. The assignment becomes immediately available to all enrolled students.

### Step 4: Grade Student Submissions (`/submissions/:id/grade`)
1. Open "Database Systems", select "ER Diagramming &amp; Conceptual Modeling", and scroll to the **Submissions Roster**.
2. Meron Girma's submission displays a yellow **Pending Review** badge.
3. Click **Grade** next to the submission.
4. Enter a numeric grade (enforced between `0` and `max_score`) and enter constructive instructor feedback.
5. Click **Submit Grade**. The submission status transitions to `graded`, and the student's dashboard updates immediately.

---

## 4. Organization Role Guide

### Demo Accounts
- **Approved Organization**: Kaffa Digital Solutions (Yohannes Haile, `yohannes.haile@example.com`)
- **Approved Organization**: Gibe Valley Telecom Services (Rahel Desta, `rahel.desta@example.com`)
- **Pending Organization**: Abay Data Labs (Eyob Kassa, `eyob.kassa@example.com`)

### Step 1: Review the Organization Dashboard (`/`)
1. Log in as `yohannes.haile@example.com`.
2. Review company metrics:
   - **Active Listings** currently accepting applications (Junior Web Developer Intern, Data Analysis Intern).
   - **Pending Review** postings in the moderation queue (Mobile Application Intern).
   - **Total Applications** received across all postings.

### Step 2: Manage Company Profile (`/profile`)
1. Navigate to **Profile** to update company information:
   - Organization Name: Kaffa Digital Solutions
   - Industry category: Software &amp; Digital Solutions
   - Location: Addis Ababa
   - Official Website URL: `https://kaffadigital.example.org`
2. Save changes to ensure student applicants see verified company details.

### Step 3: Post an Internship Listing (`/internships/new`)
1. Click **Post Internship**.
2. Fill in the job title, department, description, requirements, location, work mode (`remote`/`hybrid`/`onsite`), and application deadline.
3. Submit the listing.
   - Postings enter the `pending_review` state to allow platform administrators to verify the opportunity.
4. **Vetting Demonstration**: Log in as `eyob.kassa@example.com` (Abay Data Labs). Observe that posting creation is disabled with an explanatory banner informing the company that administrative approval is required first.

### Step 4: Candidate Pipeline &amp; Hiring Decisions (`/internships/:id`)
1. Navigate to **My Postings** (`/my-internships`) as `yohannes.haile@example.com`.
2. Select "Junior Web Developer Intern".
3. Review the **Applicants Roster** displaying applicant names, emails, skills, submission dates, and cover letters.
4. Notice hiring decisions:
   - Abel Tesfaye: **Accepted**
   - Meron Girma: **Shortlisted**
5. Click **Review Application** to advance candidate decisions. Terminal decisions lock the application against tampering.

---

## 5. Administrator Role Guide

### Demo Account
- **System Administrator**: Dr. Mulugeta Assefa (`mulugeta.assefa@example.com`)

### Step 1: Access the Administrator Dashboard (`/`)
1. Log in as `mulugeta.assefa@example.com`.
2. Inspect the high-level platform health indicators:
   - Total users across Student, Instructor, Organization, and Admin roles.
   - Pending Organization registrations requiring vetting (Abay Data Labs).
   - Pending Internship postings requiring content moderation (Mobile Application Intern).

### Step 2: User Account Administration (`/admin/users`)
1. Click **Admin** &rarr; **Users** in the navigation bar.
2. Filter accounts by role or search by name and email.
3. **Deactivation / Activation**:
   - Click **Deactivate** on an active account to revoke platform access.
   - **Self-Protection Guard**: Notice that deactivation controls are disabled on your own account (`mulugeta.assefa@example.com`) to prevent lockouts.
4. **Administrative Password Reset**:
   - Click **Reset Password** on any user row.
   - A modal generates a cryptographically secure temporary password and invalidates all existing active sessions for that account immediately.

### Step 3: Organization Vetting Queue (`/admin/organizations`)
1. Navigate to **Admin** &rarr; **Organizations**.
2. Find unverified companies (such as Abay Data Labs, contact `eyob.kassa@example.com` with status `pending_review`).
3. Click **Review**. Verify company details, description, and website.
4. Click **Approve Organization** to grant full posting privileges, or **Reject** if the company cannot be verified.

### Step 4: Internship Content Moderation (`/admin/internships`)
1. Navigate to **Admin** &rarr; **Internship Reviews**.
2. Filter listings with status `pending_review` (Mobile Application Intern).
3. Open a pending submission:
   - Click **Approve** to publish the listing directly into the student search catalog.
   - Click **Reject** and provide a mandatory review note explaining what edits are required.
4. Notice the rejected posting "Unsupervised Crypto Trading Bot Intern" with Dr. Mulugeta's moderation feedback note explaining why it was rejected.

---

## 6. Internship Coordinator Role Guide

### Demo Account
- **Internship Coordinator**: Ms. Selamawit Tadesse (`selamawit.tadesse@example.com`)

### Step 1: Access the Coordinator Dashboard (`/dashboard`)
1. Log in as `selamawit.tadesse@example.com`.
2. Review key operational moderation metrics:
   - Organizations pending review.
   - Internship postings pending moderation review.
   - Currently active open internships.
   - Applications breakdown by status across the institution.
   - Total moderation reviews completed by this coordinator.

### Step 2: Organization Approval Queue (`/admin/organizations`)
1. Click **Organizations** in the coordinator navigation bar.
2. Review unverified employer registrations (e.g. Abay Data Labs).
3. Inspect company profile credentials, industry, and website.
4. Click **Approve Organization** or **Reject** with review rationale.

### Step 3: Internship Posting Moderation (`/admin/internships`)
1. Click **Internship reviews** in the navigation bar.
2. Moderate submitted postings with status `pending_review` (e.g. Mobile Application Intern).
3. Inspect role details, requirements, work mode, and application deadline.
4. Click **Approve** to publish to students, or **Reject** with feedback for the employer.
5. Take down listings when necessary to safeguard student placements.

### Step 4: Internship Listings and Read-Only Applicant Inspection (`/internships`)
1. Click **Internships** to browse all platform listings across all statuses (`draft`, `pending_review`, `open`, `closed`, `rejected`).
2. Open any internship details page to inspect listing details and view incoming candidate applications and statuses in read-only mode.
3. Note security bounds: Coordinators cannot manage system users, reset other users' passwords, administer courses, or access system status.

---

## 7. Account Self-Service &amp; Session Management

### Changing Passwords (`/account`)
Any authenticated user can update their password:
1. Click your user avatar / email in the top navigation and select **Account Settings**.
2. Enter your current password and your new password (minimum 8 characters).
3. Upon submission, the server verifies the current hash, updates the hash, and refreshes your session.

### Logging Out
1. Click **Sign out** in the navigation bar. The server invalidates the session in PostgreSQL, clears the `HttpOnly` cookie, and redirects to `/login`.

---

## 8. In-App Notifications & Activity Tracking
The platform includes an automated in-app notifications center that keeps all personas informed of critical lifecycle events across courses, assignments, applications, and account security.

### Notification Bell & Unread Counter
- A notification bell icon is situated in the top navigation header across all authenticated views.
- If there are unread notifications, a bold petrol badge displays the exact unread count (e.g., `3`).
- **Visibility-Aware Polling**: The unread counter polls the server every 60 seconds when active, refetching instantly when window regains focus.

### Notifications Page (`/notifications`)
1. Click the notification bell icon (or navigate to `/notifications`) to open your notifications feed.
2. **Visual Indicators**: Unread notifications are distinguished with a petrol tint background, bold title, and an unread dot indicator.
3. **Deep Linking**: Click any notification to navigate directly to its related entity (e.g., assignment details, course syllabus, application decision, or internship posting).
4. **Mark as Read**:
   - Clicking a notification automatically marks it as read on the server.
   - Click the checkmark icon on an individual item to mark it as read without navigating away.
   - Click **Mark all as read** at the top right to clear all unread badges simultaneously.
5. **Retention**: The platform automatically caps history at the 200 most recent notifications per user via an automated database pruning trigger.
