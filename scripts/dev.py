#!/usr/bin/env python3
"""Run backend and frontend servers together for local development."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIR = REPO_ROOT / "frontend"


def get_backend_python() -> Path:
    venv_py = (
        BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
        if sys.platform == "win32"
        else BACKEND_DIR / ".venv" / "bin" / "python"
    )
    if venv_py.exists():
        return venv_py
    return Path(sys.executable)


def check_database_and_migrations(python_bin: Path) -> bool:
    """Verify local PostgreSQL connectivity and migration status."""
    check_script = (
        "import sys\n"
        "try:\n"
        "    from app.core.database import engine\n"
        "    from sqlalchemy import text\n"
        "    from alembic.config import Config\n"
        "    from alembic.script import ScriptDirectory\n"
        "    from alembic.runtime.migration import MigrationContext\n"
        "    with engine.connect() as conn:\n"
        "        conn.execute(text('SELECT 1'))\n"
        "        ctx = MigrationContext.configure(conn)\n"
        "        current = ctx.get_current_revision()\n"
        "    config = Config('alembic.ini')\n"
        "    head = ScriptDirectory.from_config(config).get_current_head()\n"
        "    if current != head:\n"
        "        print(f'MIGRATION_MISMATCH:current={current}:head={head}')\n"
        "        sys.exit(2)\n"
        "    print('OK')\n"
        "except Exception as e:\n"
        "    print(f'DB_ERROR:{e}')\n"
        "    sys.exit(1)\n"
    )

    res = subprocess.run(
        [str(python_bin), "-c", check_script],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
        check=False,
    )

    if res.returncode == 0:
        return True

    out = (res.stdout + "\n" + res.stderr).strip()
    if res.returncode == 2:
        print("\n[dev] Database migrations are not up to date.", file=sys.stderr)
        print(f"[dev] Details: {out}", file=sys.stderr)
        print("[dev] Run migrations before starting dev server:", file=sys.stderr)
        if sys.platform == "win32":
            print(
                r"[dev]   .\backend\.venv\Scripts\alembic.exe upgrade head",
                file=sys.stderr,
            )
        else:
            print("[dev]   backend/.venv/bin/alembic upgrade head", file=sys.stderr)
        return False

    print("\n[dev] Could not connect to local PostgreSQL.", file=sys.stderr)
    print(f"[dev] Error details: {out}", file=sys.stderr)
    print("[dev] Ensure PostgreSQL is running on port 5432:", file=sys.stderr)
    print("[dev]   docker compose up -d db", file=sys.stderr)
    print("[dev] Or configure local environment with:", file=sys.stderr)
    print("[dev]   python scripts/setup_dev.py", file=sys.stderr)
    return False


def stream_logs(proc: subprocess.Popen[str], prefix: str) -> None:
    """Stream process stdout/stderr with custom tag prefix."""
    if proc.stdout is None:
        return
    for line in iter(proc.stdout.readline, ""):
        print(f"{prefix} {line}", end="", flush=True)


def stop_process(proc: subprocess.Popen[str] | None) -> None:
    """Terminate process tree without leaving orphan processes."""
    if proc is None or proc.poll() is not None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.terminate()
            proc.wait(timeout=3)
    except (OSError, subprocess.SubprocessError):
        try:
            proc.kill()
        except (OSError, subprocess.SubprocessError):
            return


def main() -> int:
    backend_py = get_backend_python()
    npm_bin = (
        shutil.which("npm.cmd") if sys.platform == "win32" else shutil.which("npm")
    )
    if not npm_bin:
        npm_bin = "npm"

    print("[dev] Checking local database and migrations...")
    if not check_database_and_migrations(backend_py):
        return 1

    print("[dev] Starting backend (:8001) and frontend (:5173)...")
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"

    backend_cmd = [
        str(backend_py),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8001",
        "--reload",
    ]
    frontend_cmd = [npm_bin, "run", "dev"]

    flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0

    backend_proc: subprocess.Popen[str] | None = None
    frontend_proc: subprocess.Popen[str] | None = None

    def handle_shutdown(signum: int, frame: object) -> None:
        print("\n[dev] Shutting down development servers...")
        stop_process(backend_proc)
        stop_process(frontend_proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(BACKEND_DIR),
            env=backend_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=flags,
        )

        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=flags,
        )

        t_backend = threading.Thread(
            target=stream_logs, args=(backend_proc, "[backend] "), daemon=True
        )
        t_frontend = threading.Thread(
            target=stream_logs, args=(frontend_proc, "[frontend]"), daemon=True
        )

        t_backend.start()
        t_frontend.start()

        while True:
            b_code = backend_proc.poll()
            f_code = frontend_proc.poll()
            if b_code is not None:
                print(f"[dev] Backend exited with code {b_code}", file=sys.stderr)
                break
            if f_code is not None:
                print(f"[dev] Frontend exited with code {f_code}", file=sys.stderr)
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        stop_process(backend_proc)
        stop_process(frontend_proc)
        print("[dev] Development servers stopped cleanly.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
