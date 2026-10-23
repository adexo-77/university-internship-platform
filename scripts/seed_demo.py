#!/usr/bin/env python3
"""Idempotent demo dataset seeder for the University Learning & Internship Platform."""

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "scripts"
for d in (BACKEND_DIR, SCRIPTS_DIR):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from seed_demo_academics import seed_academics
from seed_demo_internships import seed_internships_and_apps
from seed_demo_reset import reset_demo
from seed_demo_users import seed_demo_users_and_profiles

DEMO_PASSWORD = "12345678"


def seed_demo(db: Session, force: bool = False) -> None:
    env = os.environ.get("ENVIRONMENT", settings.ENVIRONMENT).strip().lower()
    if env == "production" and not force:
        print(
            "Error: seed_demo refuses to run in production without --force.",
            file=sys.stderr,
        )
        sys.exit(1)

    now = datetime.now(UTC)
    pw_hash = hash_password(DEMO_PASSWORD)
    users = seed_demo_users_and_profiles(db, pw_hash)
    seed_academics(db, users, now)
    seed_internships_and_apps(db, users, now)
    db.commit()
    print("Demo dataset seeded successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo dataset into the database.")
    parser.add_argument("--force", action="store_true", help="Force run in production.")
    parser.add_argument(
        "--reset-demo",
        action="store_true",
        help="Remove all demo accounts in foreign-key dependency order.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt for demo reset.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset_demo:
            reset_demo(db, skip_confirm=args.yes)
        else:
            seed_demo(db, force=args.force)
    finally:
        db.close()


if __name__ == "__main__":
    main()
