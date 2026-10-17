"""CLI administrative tool to create instructor and admin accounts."""

import argparse
import getpass
import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Ensure backend directory is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from sqlalchemy import select

ALLOWED_ROLES = (UserRole.INSTRUCTOR.value, UserRole.ADMIN.value)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create an instructor or admin account directly in the database."
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Email address of the user (will be stored lowercase)",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Full name of the user",
    )
    parser.add_argument(
        "--role",
        required=True,
        choices=ALLOWED_ROLES,
        help="Account role (must be 'instructor' or 'admin')",
    )
    return parser.parse_args()


def main(db_session: Session | None = None) -> None:
    """Main CLI execution flow."""
    args = parse_args()
    normalized_email = args.email.strip().lower()
    full_name = args.name.strip()
    role_str = args.role.strip()

    if not normalized_email or "@" not in normalized_email:
        print("Error: A valid email address is required.", file=sys.stderr)
        sys.exit(1)

    if not full_name:
        print("Error: Full name cannot be blank.", file=sys.stderr)
        sys.exit(1)

    # Read password safely with getpass (never passed as CLI argument or printed)
    password = getpass.getpass("Enter password (8-128 characters): ")
    if len(password) < 8 or len(password) > 128:
        print(
            "Error: Password must be between 8 and 128 characters.",
            file=sys.stderr,
        )
        sys.exit(1)

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Error: Passwords do not match.", file=sys.stderr)
        sys.exit(1)

    should_close_db = db_session is None
    db = db_session if db_session is not None else SessionLocal()
    try:
        existing_user = db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            print(
                f"User with email '{normalized_email}' already exists "
                f"(Role: {existing_user.role.value}). No duplicate created."
            )
            return

        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole(role_str),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(
            f"Successfully created {role_str} user '{normalized_email}' "
            f"(ID: {user.id})."
        )
    finally:
        if should_close_db:
            db.close()


if __name__ == "__main__":
    main()
