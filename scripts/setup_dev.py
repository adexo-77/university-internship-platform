#!/usr/bin/env python3
"""Cross-platform, idempotent developer setup tool using Python standard library only."""

import argparse
import getpass
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

MIN_PYTHON_VERSION = (3, 12)
MIN_NODE_VERSION = 18
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIR = REPO_ROOT / "frontend"


def get_venv_paths() -> tuple[Path, Path]:
    venv_dir = BACKEND_DIR / ".venv"
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe", venv_dir / "Scripts" / "alembic.exe"
    return venv_dir / "bin" / "python", venv_dir / "bin" / "alembic"


def check_prerequisites() -> None:
    if sys.version_info < MIN_PYTHON_VERSION:
        v = f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
        print(
            f"Error: Python {v}+ is required. Current: {sys.version.split()[0]}",
            file=sys.stderr,
        )
        sys.exit(1)

    node_bin = shutil.which("node")
    if not node_bin:
        print("Error: Node.js is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

    try:
        node_out = subprocess.check_output([node_bin, "-v"], text=True).strip()
        m = re.search(r"v?(\d+)", node_out)
        if not m or int(m.group(1)) < MIN_NODE_VERSION:
            print(
                f"Error: Node {MIN_NODE_VERSION}+ required. Found: {node_out}",
                file=sys.stderr,
            )
            sys.exit(1)
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error checking Node version: {e}", file=sys.stderr)
        sys.exit(1)


def setup_venv_and_dependencies() -> None:
    venv_dir = BACKEND_DIR / ".venv"
    venv_python, _ = get_venv_paths()

    if not venv_python.exists():
        print(f"Creating Python virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    print("Installing backend dependencies...")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True
    )
    subprocess.run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(BACKEND_DIR / "requirements.txt"),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(BACKEND_DIR / "requirements-dev.txt"),
        ],
        check=True,
    )

    npm_bin = shutil.which("npm")
    if not npm_bin:
        print("Error: npm not found in PATH.", file=sys.stderr)
        sys.exit(1)

    print("Installing frontend dependencies (npm install)...")
    subprocess.run([npm_bin, "install"], cwd=str(FRONTEND_DIR), check=True)


def ensure_env_file() -> None:
    env_file = REPO_ROOT / ".env"
    env_example = REPO_ROOT / ".env.example"

    if env_file.exists():
        print(".env file already exists. Leaving unchanged.")
        return

    if not env_example.exists():
        print("Error: .env.example missing.", file=sys.stderr)
        sys.exit(1)

    print("\nNo .env file found. Configuring from .env.example...")
    prompt = "Enter PostgreSQL password for user 'postgres' (blank for 'postgres'): "
    try:
        pg_pass = getpass.getpass(prompt) or "postgres"
    except (getpass.GetPassWarning, EOFError, OSError):
        pg_pass = "postgres"

    enc_pass = urllib.parse.quote_plus(pg_pass)
    content = env_example.read_text(encoding="utf-8")
    new_content = content.replace("postgres:postgres@", f"postgres:{enc_pass}@")
    env_file.write_text(new_content, encoding="utf-8")
    print("Created .env with URL-encoded database credentials.\n")


def parse_db_names_and_urls() -> tuple[str, str, str]:
    env_file = REPO_ROOT / ".env"
    db_url = ""
    test_db_url = ""
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("DATABASE_URL="):
            db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("TEST_DATABASE_URL="):
            test_db_url = line.split("=", 1)[1].strip().strip('"').strip("'")

    db_name = (
        db_url.rsplit("/", 1)[-1].split("?")[0]
        if "/" in db_url
        else "university_platform"
    )
    test_db_name = (
        test_db_url.rsplit("/", 1)[-1].split("?")[0]
        if "/" in test_db_url
        else "university_platform_test"
    )
    raw_url = db_url.replace("postgresql+psycopg://", "postgresql://")
    parsed = urllib.parse.urlparse(raw_url)
    maint_url = urllib.parse.urlunparse(parsed._replace(path="/postgres"))
    return maint_url, db_name, test_db_name


def ensure_databases() -> None:
    venv_python, _ = get_venv_paths()
    maint_url, db_name, test_db_name = parse_db_names_and_urls()

    script = (
        "import sys, psycopg\n"
        "maint_url = sys.argv[1]\n"
        "db_names = [sys.argv[2], sys.argv[3]]\n"
        "try:\n"
        "    with psycopg.connect(maint_url, autocommit=True) as conn:\n"
        "        with conn.cursor() as cur:\n"
        "            for name in db_names:\n"
        "                cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (name,))\n"
        "                if not cur.fetchone():\n"
        "                    cur.execute(f'CREATE DATABASE \"{name}\"')\n"
        "                    print(f'Created database: {name}')\n"
        "                else:\n"
        "                    print(f'Database already exists: {name}')\n"
        "except Exception as e:\n"
        "    print(f'Database connectivity notice: {e}', file=sys.stderr)\n"
    )

    subprocess.run(
        [str(venv_python), "-c", script, maint_url, db_name, test_db_name],
        check=False,
    )


def run_migrations_and_optional_seed(seed: bool) -> None:
    venv_python, venv_alembic = get_venv_paths()
    print("Running database migrations (alembic upgrade head)...")
    subprocess.run(
        [str(venv_alembic), "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        check=True,
    )

    if seed:
        print("Seeding demo dataset (--seed)...")
        seed_script = REPO_ROOT / "scripts" / "seed_demo.py"
        subprocess.run(
            [str(venv_python), str(seed_script)], cwd=str(REPO_ROOT), check=True
        )


def print_run_instructions(seeded: bool = False) -> None:
    is_win = sys.platform == "win32"
    act_cmd = r".\.venv\Scripts\Activate.ps1" if is_win else "source .venv/bin/activate"
    print("\n" + "=" * 60)
    print("Developer environment setup successfully completed!")
    print("=" * 60)
    if seeded:
        print("\nDemo Accounts Seeded (password: 12345678 - demo only):")
        print("  Admin:        Dr. Mulugeta Assefa     <mulugeta.assefa@example.com>")
        print("  Instructor:   Dr. Tadesse Bekele      <tadesse.bekele@example.com>")
        print("  Student:      Abel Tesfaye            <abel.tesfaye@example.com>")
        print("  Organization: Kaffa Digital Solutions <yohannes.haile@example.com>")
    print("\nTo run the backend development server:")
    print("  Set-Location backend" if is_win else "  cd backend")
    print(f"  {act_cmd}")
    print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload")
    print("\nTo run the frontend development server:")
    print("  Set-Location frontend" if is_win else "  cd frontend")
    print("  npm run dev")
    print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Developer environment setup tool.")
    parser.add_argument(
        "--seed", action="store_true", help="Seed demo dataset after setup."
    )
    args = parser.parse_args()

    check_prerequisites()
    setup_venv_and_dependencies()
    ensure_env_file()
    ensure_databases()
    run_migrations_and_optional_seed(seed=args.seed)
    print_run_instructions(seeded=args.seed)


if __name__ == "__main__":
    main()
