"""Test that docs/openapi.json exists and matches the FastAPI app schema."""

import json
from pathlib import Path

from app.main import app


def test_openapi_json_is_up_to_date() -> None:
    """Validate that docs/openapi.json is synchronized with FastAPI app.openapi().

    If this test fails, run:
        python scripts/export_openapi.py
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    openapi_file = repo_root / "docs" / "openapi.json"

    assert openapi_file.is_file(), (
        f"docs/openapi.json not found at {openapi_file}. "
        "Run 'python scripts/export_openapi.py' to generate it."
    )

    disk_content = openapi_file.read_text(encoding="utf-8")
    disk_schema = json.loads(disk_content)
    current_schema = app.openapi()

    assert disk_schema == current_schema, (
        "docs/openapi.json is out of date with app.openapi(). "
        "Run 'python scripts/export_openapi.py' to synchronize the specification."
    )

    # Also verify deterministic formatting and newline
    expected_content = json.dumps(current_schema, indent=2, ensure_ascii=False) + "\n"
    assert disk_content == expected_content, (
        "docs/openapi.json formatting differs from deterministic export. "
        "Run 'python scripts/export_openapi.py' to reformat."
    )
