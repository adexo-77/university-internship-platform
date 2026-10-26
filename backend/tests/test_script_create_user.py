"""Tests for scripts/create_user.py CLI tool."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure repository root is on sys.path to import scripts
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.create_user import main  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.models.user import User, UserRole  # noqa: E402


def test_create_user_script_via_getpass(real_db_session: Session) -> None:
    test_args = [
        "create_user.py",
        "--email",
        "  New.Instructor@Example.COM  ",
        "--name",
        "Dr. Test Instructor",
        "--role",
        "instructor",
    ]

    with (
        patch("sys.argv", test_args),
        patch(
            "getpass.getpass",
            side_effect=["InstructorPass123!", "InstructorPass123!"],
        ),
        patch.dict(os.environ, {}, clear=True),
    ):
        main(db_session=real_db_session)

    user = real_db_session.scalar(select(User).where(User.email == "new.instructor@example.com"))
    assert user is not None
    assert user.role == UserRole.INSTRUCTOR
    assert user.full_name == "Dr. Test Instructor"
    assert user.is_active is True

    # Running it a second time with the same email must not create a duplicate
    with (
        patch("sys.argv", test_args),
        patch(
            "getpass.getpass",
            side_effect=["InstructorPass123!", "InstructorPass123!"],
        ),
        patch.dict(os.environ, {}, clear=True),
    ):
        main(db_session=real_db_session)

    users = real_db_session.scalars(
        select(User).where(User.email == "new.instructor@example.com")
    ).all()
    assert len(users) == 1


def test_create_user_script_via_env_var(real_db_session: Session) -> None:
    test_args = [
        "create_user.py",
        "--email",
        "coordinator.env@example.com",
        "--name",
        "Coordinator Env",
        "--role",
        "coordinator",
    ]

    with (
        patch("sys.argv", test_args),
        patch.dict(os.environ, {"CREATE_USER_PASSWORD": "CoordinatorSecure123!"}),
    ):
        main(db_session=real_db_session)

    user = real_db_session.scalar(select(User).where(User.email == "coordinator.env@example.com"))
    assert user is not None
    assert user.role == UserRole.COORDINATOR
    assert user.full_name == "Coordinator Env"


def test_create_user_script_rejects_cli_password_argument(real_db_session: Session) -> None:
    test_args = [
        "create_user.py",
        "--email",
        "bad.arg@example.com",
        "--name",
        "Bad Arg",
        "--role",
        "admin",
        "--password",
        "PlaintextInCommandLine",
    ]

    with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
        main(db_session=real_db_session)

    assert exc_info.value.code != 0
