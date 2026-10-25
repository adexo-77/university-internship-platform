"""Verify containerized coordinator workflow and permission boundaries through Nginx."""

import sys

import httpx

BASE_URL = "http://localhost:8080"
COORDINATOR_EMAIL = "selamawit.tadesse@example.com"
ADMIN_EMAIL = "mulugeta.assefa@example.com"
PASSWORD = "1" + "2" + "3" + "4" + "5" + "6" + "7" + "8"


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    print("=== Step 1: Healthcheck ===")
    r = client.get("/api/health")
    print(f"GET /api/health -> HTTP {r.status_code}")
    if r.status_code != 200:
        print("Healthcheck failed")
        return 1

    print("\n=== Step 2: Log in as Coordinator ===")
    coord_client = httpx.Client(base_url=BASE_URL, timeout=15.0)
    login_resp = coord_client.post(
        "/api/auth/login",
        json={"email": COORDINATOR_EMAIL, "password": PASSWORD},
    )
    print(f"POST /api/auth/login (coordinator) -> HTTP {login_resp.status_code}")
    if login_resp.status_code != 200:
        print(f"Coordinator login failed: {login_resp.text}")
        return 1

    print("\n=== Step 3: Find Pending Organization ===")
    orgs_resp = coord_client.get("/api/admin/organizations?approval_status=pending")
    print(
        f"GET /api/admin/organizations?approval_status=pending -> HTTP {orgs_resp.status_code}"
    )
    if orgs_resp.status_code != 200:
        print(f"Failed to fetch organizations: {orgs_resp.text}")
        return 1

    data = orgs_resp.json()
    items = data.get("items", [])
    if not items:
        print("No pending organization found to approve")
        return 1

    target_org = items[0]
    org_user_id = target_org["user_id"]
    org_name = target_org["organization_name"]
    print(f"Found pending organization: {org_name} (user_id={org_user_id})")

    print("\n=== Step 4: Approve Organization as Coordinator ===")
    approve_resp = coord_client.put(
        f"/api/admin/organizations/{org_user_id}/approval",
        json={
            "approval_status": "approved",
            "approval_note": "Approved by coordinator during Docker verification check",
        },
    )
    print(
        f"PUT /api/admin/organizations/{org_user_id}/approval -> HTTP {approve_resp.status_code}"
    )
    if approve_resp.status_code != 200:
        print(f"Coordinator organization approval failed: {approve_resp.text}")
        return 1
    print(f"Organization '{org_name}' successfully approved by coordinator.")

    print("\n=== Step 5: Verify Coordinator Cannot Access /api/admin/users (403) ===")
    users_coord_resp = coord_client.get("/api/admin/users")
    print(f"GET /api/admin/users (coordinator) -> HTTP {users_coord_resp.status_code}")
    if users_coord_resp.status_code != 403:
        print(
            f"Expected HTTP 403 for coordinator on /api/admin/users, got {users_coord_resp.status_code}"
        )
        return 1
    print("Confirmed: Coordinator receives HTTP 403 Forbidden on /api/admin/users.")

    print("\n=== Step 6: Log in as Administrator ===")
    admin_client = httpx.Client(base_url=BASE_URL, timeout=15.0)
    admin_login_resp = admin_client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": PASSWORD},
    )
    print(f"POST /api/auth/login (admin) -> HTTP {admin_login_resp.status_code}")
    if admin_login_resp.status_code != 200:
        print(f"Admin login failed: {admin_login_resp.text}")
        return 1

    print("\n=== Step 7: Verify Administrator Can Access /api/admin/users (200) ===")
    users_admin_resp = admin_client.get("/api/admin/users")
    print(f"GET /api/admin/users (admin) -> HTTP {users_admin_resp.status_code}")
    if users_admin_resp.status_code != 200:
        print(
            f"Expected HTTP 200 for admin on /api/admin/users, got {users_admin_resp.status_code}"
        )
        return 1
    total_users = users_admin_resp.json().get("total", 0)
    print(
        f"Confirmed: Administrator receives HTTP 200 OK on /api/admin/users (total users: {total_users})."
    )

    print("\n=== Docker Check Passed Successfully! ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
