"""Inspect and print real demo facts from the running Docker API."""

from __future__ import annotations

import json
import urllib.request
from http.cookiejar import CookieJar

BASE_URL = "http://127.0.0.1:8080"
DEMO_PASSWORD = "12345678"

DEMO_ACCOUNTS = [
    ("mulugeta.assefa@example.com", "admin", "Dr. Mulugeta Assefa"),
    ("selamawit.tadesse@example.com", "coordinator", "Ms. Selamawit Tadesse"),
    ("tadesse.bekele@example.com", "instructor", "Dr. Tadesse Bekele"),
    ("hana.worku@example.com", "instructor", "Ms. Hana Worku"),
    ("abel.tesfaye@example.com", "student", "Abel Tesfaye"),
    ("meron.girma@example.com", "student", "Meron Girma"),
    ("dawit.lemma@example.com", "student", "Dawit Lemma"),
    ("yohannes.haile@example.com", "organization", "Yohannes Haile (Kaffa Digital)"),
    ("rahel.desta@example.com", "organization", "Rahel Desta (Gibe Valley)"),
    ("eyob.kassa@example.com", "organization", "Eyob Kassa (Abay Data Labs)"),
]


class ApiSession:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def request(
        self, method: str, path: str, data: dict | None = None
    ) -> tuple[int, dict]:
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with self.opener.open(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}


def inspect_account(email: str, role: str, name: str) -> None:
    session = ApiSession(BASE_URL)
    status, _ = session.request(
        "POST", "/api/auth/login", {"email": email, "password": DEMO_PASSWORD}
    )
    if status != 200:
        print(f"FAILED TO LOGIN: {email}")
        return

    print(
        "================================================================================"
    )
    print(f"ACCOUNT: {name} <{email}> (Role: {role})")
    print(
        "================================================================================"
    )

    if role == "student":
        # 1. Enrolled courses
        _, dash = session.request("GET", "/api/dashboard/student")
        courses = [
            f"Course #{c['course_id']} - {c['title']} (progress: {c['progress_percent']}%, avg: {c.get('average_grade_percent')}%)"
            for c in dash.get("courses", [])
        ]
        print(f"Enrolled Courses ({len(courses)}):")
        for c in courses:
            print(f"  - {c}")

        # 2. Applications
        _, apps = session.request("GET", "/api/students/me/applications")
        print(f"Applications ({len(apps)}):")
        for a in apps:
            p_title = a.get("posting_title") or a.get("title")
            org_name = a.get("organization_name", "N/A")
            st = a.get("status")
            print(f'  - "{p_title}" at {org_name} -> STATUS: {st}')

        # 3. Badges
        _, badges = session.request("GET", "/api/students/me/badges")
        earned = [b for b in badges if b.get("earned")]
        unearned = [b for b in badges if not b.get("earned")]
        print(f"Badges Earned ({len(earned)} of {len(badges)}):")
        for b in earned:
            prog_str = ""
            if b.get("progress") and b["progress"].get("target"):
                prog_str = (
                    f" [progress: {b['progress']['current']}/{b['progress']['target']}]"
                )
            print(f"  - [EARNED] id='{b['id']}', title='{b['title']}'{prog_str}")
        print(f"Badges In-Progress / Unearned ({len(unearned)}):")
        for b in unearned:
            prog_str = ""
            if b.get("progress") and b["progress"].get("target"):
                prog_str = (
                    f" [progress: {b['progress']['current']}/{b['progress']['target']}]"
                )
            print(f"  - [LOCKED] id='{b['id']}', title='{b['title']}'{prog_str}")

        # 4. Study Plan summary
        _, plan = session.request("GET", "/api/students/me/study-plan?days=7")
        summary = plan.get("summary", {})
        print(f'Study Plan Headline: "{summary.get("headline")}"')
        print("Study Plan Sentences:")
        for s in summary.get("sentences", []):
            print(f"    * {s}")

    elif role == "instructor":
        _, dash = session.request("GET", "/api/dashboard/instructor")
        courses = dash.get("courses", [])
        needs_grading = dash.get("needs_grading", [])
        total_awaiting = sum(c.get("submissions_awaiting_grading", 0) for c in courses)
        print(f"Authored Courses ({len(courses)}):")
        for c in courses:
            print(
                f"  - Course #{c['course_id']} - {c['title']} (status: {c['status']}, "
                f"enrolled: {c['enrolled_count']}, "
                f"assignments: {c['assignments_count']}, "
                f"awaiting_grading: {c['submissions_awaiting_grading']})"
            )
        print(
            f"Submissions Awaiting Grading (Total: {total_awaiting}, Queue Length: {len(needs_grading)}):"
        )
        for ng in needs_grading:
            print(
                f"  - Submission #{ng.get('submission_id')}: student='{ng.get('student_name')}' | "
                f"assignment='{ng.get('assignment_title')}' (course: '{ng.get('course_title')}') | "
                f"late={ng.get('late')}"
            )

    elif role == "organization":
        _, dash = session.request("GET", "/api/dashboard/organization")
        postings = dash.get("postings", {}).get("active", [])
        recent_apps = dash.get("recent_applications", [])
        print(f"Active Postings ({len(postings)}):")
        for p in postings:
            print(
                f'  - Posting #{p["posting_id"]}: "{p["title"]}" (applicants: {p["applicant_count"]})'
            )
        print(
            f"Applications Awaiting Decision: {dash.get('applications_awaiting_decision')}"
        )
        print(f"Recent Applications Received ({len(recent_apps)}):")
        for ra in recent_apps:
            print(
                f"  - Application #{ra['application_id']}: student='{ra['applicant_name']}', posting='{ra['posting_title']}', status='{ra['status']}'"
            )

    elif role == "coordinator":
        _, dash = session.request("GET", "/api/dashboard/coordinator")
        print(
            f"Organizations Pending Approval: {dash.get('organizations_pending_approval')}"
        )
        print(f"Internships Pending Review: {dash.get('internships_pending_review')}")
        print(f"Open Internships: {dash.get('open_internships')}")
        print(f"Applications by Status: {dash.get('applications_by_status')}")
        print(f"Reviews Completed: {dash.get('reviews_completed')}")

    elif role == "admin":
        _, dash = session.request("GET", "/api/dashboard/admin")
        print(
            f"Total Users: {dash.get('users_total_count')} (Active: {dash.get('users_active_count')})"
        )
        print(f"Users by Role: {dash.get('users_by_role')}")
        print(
            f"Organizations Pending Approval: {dash.get('organizations_pending_approval')}"
        )
        print(f"Postings Pending Review: {dash.get('postings_pending_review')}")
        print(f"Open Internships: {dash.get('open_internships')}")
        print(f"Courses by Status: {dash.get('courses_by_status')}")
        print(f"Applications by Status: {dash.get('applications_by_status')}")

    session.request("POST", "/api/auth/logout")
    print()


def main() -> None:
    for email, role, name in DEMO_ACCOUNTS:
        inspect_account(email, role, name)


if __name__ == "__main__":
    main()
