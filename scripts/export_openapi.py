#!/usr/bin/env python3
"""Export FastAPI OpenAPI JSON schema to docs/openapi.json."""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
DOCS_DIR = REPO_ROOT / "docs"
OUTPUT_FILE = DOCS_DIR / "openapi.json"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


def generate_openapi_json() -> str:
    """Generate deterministic, formatted OpenAPI JSON from FastAPI app."""
    schema = app.openapi()
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def export_openapi(target_path: Path = OUTPUT_FILE) -> Path:
    """Write OpenAPI schema to the target path."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate_openapi_json()
    target_path.write_text(content, encoding="utf-8", newline="\n")
    return target_path


def main() -> None:
    """CLI entrypoint."""
    path = export_openapi()
    print(f"Successfully exported OpenAPI schema to {path}")


if __name__ == "__main__":
    main()
