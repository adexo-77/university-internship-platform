#!/usr/bin/env python3
"""Verification script for demo accounts across API and SPA frontend."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

DEMO_PASSWORD = "12345678"

DEMO_ACCOUNTS: list[tuple[str, str, str]] = [
    ("mulugeta.assefa@example.com", "Dr. Mulugeta Assefa", "admin"),
    ("selamawit.tadesse@example.com", "Ms. Selamawit Tadesse", "coordinator"),
    ("tadesse.bekele@example.com", "Dr. Tadesse Bekele", "instructor"),
    ("hana.worku@example.com", "Ms. Hana Worku", "instructor"),
    ("abel.tesfaye@example.com", "Abel Tesfaye", "student"),
    ("meron.girma@example.com", "Meron Girma", "student"),
    ("dawit.lemma@example.com", "Dawit Lemma", "student"),
    ("yohannes.haile@example.com", "Yohannes Haile", "organization"),
    ("rahel.desta@example.com", "Rahel Desta", "organization"),
    ("eyob.kassa@example.com", "Eyob Kassa", "organization"),
]


class DemoClient:
    """HTTP client maintaining session cookies across requests."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict | str]:
        url = f"{self.base_url}{path}"
        req_headers = {"User-Agent": "VerifyDemoScript/1.0"}
        if headers:
            req_headers.update(headers)

        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with self.opener.open(req) as resp:
                status = resp.status
                raw = resp.read().decode("utf-8")
                ctype = resp.headers.get("Content-Type", "")
                if "application/json" in ctype:
                    return status, json.loads(raw)
                return status, raw
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = raw
            return exc.code, payload


def verify_account(
    base_url: str, email: str, name: str, expected_role: str
) -> dict[str, str]:
    """Test full login, identity, dashboard, notifications, and SPA home page."""
    client = DemoClient(base_url)
    res = {
        "account": name,
        "role": expected_role,
        "login": "FAIL",
        "dashboard": "FAIL",
        "notifications": "FAIL",
        "home": "FAIL",
        "passed": "false",
    }

    # 1. Login
    status, _ = client.request(
        "POST", "/api/auth/login", {"email": email, "password": DEMO_PASSWORD}
    )
    if status != 200:
        res["login"] = f"ERR {status}"
        return res
    res["login"] = "200 OK"

    # 2. Check /api/auth/me
    status, me_data = client.request("GET", "/api/auth/me")
    if (
        status != 200
        or not isinstance(me_data, dict)
        or me_data.get("role") != expected_role
    ):
        res["login"] = (
            f"ROLE_ERR ({me_data.get('role') if isinstance(me_data, dict) else status})"
        )
        return res

    # 3. Role dashboard
    dash_path = f"/api/dashboard/{expected_role}"
    status, _ = client.request("GET", dash_path)
    if status != 200:
        res["dashboard"] = f"ERR {status}"
        return res
    res["dashboard"] = "200 OK"

    # 4. Notifications
    status, _ = client.request("GET", "/api/notifications")
    if status != 200:
        res["notifications"] = f"ERR {status}"
        return res
    res["notifications"] = "200 OK"

    # 5. SPA home page (HTML)
    status, html_content = client.request(
        "GET", "/", headers={"Accept": "text/html,application/xhtml+xml"}
    )
    if (
        status != 200
        or not isinstance(html_content, str)
        or "<html" not in html_content.lower()
    ):
        res["home"] = f"ERR {status}"
        return res
    res["home"] = "200 OK"

    res["passed"] = "true"
    return res


def print_table(results: list[dict[str, str]]) -> None:
    """Print clean aligned verification table."""
    headers = ("Account", "Role", "Login", "Dashboard", "Notifications", "Home Page")
    fmt = "{:<24} | {:<12} | {:<10} | {:<10} | {:<14} | {:<10}"
    divider = "-" * 90
    print(divider)
    print(fmt.format(*headers))
    print(divider)
    for r in results:
        print(
            fmt.format(
                r["account"],
                r["role"],
                r["login"],
                r["dashboard"],
                r["notifications"],
                r["home"],
            )
        )
    print(divider)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify seeded demo accounts across API and frontend."
    )
    parser.add_argument(
        "--base-url", default="http://localhost:8080", help="Base URL of application."
    )
    args = parser.parse_args()

    print(f"Verifying {len(DEMO_ACCOUNTS)} demo accounts at {args.base_url}...\n")
    results = [
        verify_account(args.base_url, email, name, role)
        for email, name, role in DEMO_ACCOUNTS
    ]
    print_table(results)

    all_passed = all(r["passed"] == "true" for r in results)
    if all_passed:
        print("\nAll demo accounts verified successfully.")
        return 0

    print("\nOne or more demo account checks failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
