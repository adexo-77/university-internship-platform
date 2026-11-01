# Deployment &amp; Demo Sharing Guide

This document describes how to share the containerized platform temporarily over the internet using Cloudflare Quick Tunnels, the operational constraints of ephemeral sharing, security protections in public demo mode, and the upgrade path to permanent production hosting.

---

## 1. Ephemeral Sharing with Cloudflare Quick Tunnels

The platform can be made accessible over the internet without configuring firewall port forwarding, acquiring static IP addresses, or registering custom domain names.

The automated PowerShell script `scripts/share-demo.ps1` orchestrates the local stack and runs `cloudflared`:

```powershell
# Share the demo for 2 hours (default)
powershell -File .\scripts\share-demo.ps1

# Share for 60 minutes with automatic cleanup on exit
powershell -File .\scripts\share-demo.ps1 -Minutes 60 -ResetAfter

# Restrict access to designated email addresses via Cloudflare OTP
powershell -File .\scripts\share-demo.ps1 -AllowedMail "reviewer@example.com,lead@example.org"
```

When invoked, the script:
1. Verifies `cloudflared` is installed and available in `PATH`.
2. Checks whether the container stack is active; if down, starts containers with `DEMO_PUBLIC_MODE=true`.
3. Launches a Cloudflare Quick Tunnel forwarding traffic to `http://localhost:8080`.
4. Displays an operational warning and runs an active countdown timer.
5. Terminates the tunnel cleanly upon timeout expiration or when `Ctrl+C` is pressed.
6. Optionally resets container state via `docker compose down -v` if `-ResetAfter` is specified.

---

## 2. Operational Constraints &amp; Tunnel Limits

Ephemeral Quick Tunnels are intended exclusively for short-term review and client demonstrations. They are subject to the following technical constraints:

- **No Uptime Guarantee**: Quick Tunnel hostnames are ephemeral and randomized per execution. Terminating the process destroys the route permanently.
- **Concurrency Limit**: Cloudflare enforces an edge ceiling of 200 concurrent connections per free quick tunnel.
- **Protocol Restrictions**: Server-Sent Events (SSE) and raw socket protocols are not supported. Only standard HTTP/HTTPS request-response flows and basic WebSockets are proxied.
- **Host Availability**: The host computer must remain powered on, awake, and connected to the internet. Sleep mode or network disruption severs the tunnel connection.

---

## 3. Public Demo Security Controls

When sharing the platform with external reviewers, the backend operates in **Public Demo Mode** (`DEMO_PUBLIC_MODE=true`), enforcing account protections:

1. **Demo Account Immutability**:
   The ten seeded demo accounts cannot have their passwords changed or reset via administrative tools (`403 Forbidden: Disabled in the public demo`).
2. **Account Deactivation Protection**:
   Seeded demo accounts cannot be deactivated (`403 Forbidden`).
3. **Role Lock**:
   Seeded demo account roles cannot be modified (`403 Forbidden`).
4. **Privileged Account Creation Restrictions**:
   Administrators cannot provision new `admin` or `coordinator` accounts (`403 Forbidden`). Creating non-privileged instructor accounts remains enabled.
5. **UI Transparency**:
   A visible notice banner is displayed across the top of all pages indicating fictional demo data.
6. **Teardown &amp; Session Cleanup**:
   Stopping the tunnel halts external ingress immediately. Using `-ResetAfter` clears all database changes made during the session.

---

## 4. Access-Restricted Sharing

To restrict demo access to authorized parties rather than opening the URL to the general public, pass the `-AllowedMail` flag:

```powershell
powershell -File .\scripts\share-demo.ps1 -AllowedMail "reviewer@example.com"
```

Cloudflare intercepts all requests and requires visitors to enter a one-time passcode (OTP) delivered to the authorized email address before admitting traffic to the tunnel.

---

## 5. Production Hosting Upgrade Path

For permanent hosting or institutional deployment, transition from ephemeral quick tunnels to managed infrastructure:

1. **Named Cloudflare Tunnel**:
   - Provision a permanent tunnel via `cloudflared tunnel create <tunnel-name>`.
   - Route traffic through an institutional apex domain or subdomain (e.g., `internships.university.edu`).
2. **Cloudflare Access (Zero Trust)**:
   - Configure identity-provider integration (Google Workspace, Microsoft Entra ID, or Okta).
   - Enforce multi-factor authentication and role-based access policies at Cloudflare edge.
3. **Dedicated Infrastructure**:
   - Deploy Docker Compose or Kubernetes pods to a managed cloud VM or cluster.
   - Configure reverse proxy (Nginx or Traefik) terminating TLS with Let's Encrypt certificates.
   - Set `ENVIRONMENT=production`, enable `COOKIE_SECURE=true`, set strong non-default `SECRET_KEY`, and connect to a managed PostgreSQL cluster with automated backups.
