"""Test scanning README and docs for forbidden terms and valid test citations."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
DOCS_MD = list(DOCS_DIR.glob("*.md"))
README = ROOT / "README.md"
ALL_MD = [README, *DOCS_MD]

FORBIDDEN_TERMS: list[tuple[str, re.Pattern[str]]] = [
    ("argon", re.compile(r"argon", re.IGNORECASE)),
    ("pwdlib", re.compile(r"pwdlib", re.IGNORECASE)),
    ("bcrypt", re.compile(r"bcrypt", re.IGNORECASE)),
    ("GPA", re.compile(r"\bGPA\b", re.IGNORECASE)),
    ("brolf", re.compile(r"brolf", re.IGNORECASE)),
    ("evaluator", re.compile(r"evaluator", re.IGNORECASE)),
    ("production-grade", re.compile(r"production-grade", re.IGNORECASE)),
]

EMOJI_RE = re.compile(r"[\U0001f300-\U0001f9ff\u2600-\u26ff\u2700-\u27bf]")

BACKEND_TEST_RE = re.compile(r"\b(test_[a-zA-Z0-9_]+\.py)\b")
FRONTEND_TEST_RE = re.compile(r"\b([a-zA-Z0-9_-]+\.test\.tsx?)\b")


def test_no_forbidden_terms_in_docs() -> None:
    """Verify README.md and docs/*.md do not contain forbidden claims or terms."""
    violations: list[str] = []
    for doc_path in ALL_MD:
        text = doc_path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_TERMS:
            for match in pattern.finditer(text):
                line_num = text[: match.start()].count("\n") + 1
                matched = match.group()
                violations.append(f"[{label}] {doc_path.name}:{line_num}: {matched!r}")
    assert not violations, "Forbidden terms found:\n" + "\n".join(violations)


def test_no_emoji_in_docs() -> None:
    """Verify README.md and docs/*.md do not contain emojis or pictographs."""
    violations: list[str] = []
    for doc_path in ALL_MD:
        text = doc_path.read_text(encoding="utf-8")
        for match in EMOJI_RE.finditer(text):
            line_num = text[: match.start()].count("\n") + 1
            char = match.group()
            violations.append(f"{doc_path.name}:{line_num}: U+{ord(char):04X} {char!r}")
    assert not violations, "Emoji or pictographs found:\n" + "\n".join(violations)


def test_requirements_md_test_paths_exist() -> None:
    """Verify every backend and frontend test file cited in requirements exists."""
    req_path = ROOT / "docs" / "requirements.md"
    assert req_path.is_file(), "docs/requirements.md must exist"
    text = req_path.read_text(encoding="utf-8")

    missing: list[str] = []
    backend_tests = set(BACKEND_TEST_RE.findall(text))
    backend_test_dir = ROOT / "backend" / "tests"

    for test_file in backend_tests:
        if not (backend_test_dir / test_file).is_file():
            missing.append(f"backend/tests/{test_file}")

    frontend_tests = set(FRONTEND_TEST_RE.findall(text))
    frontend_src = ROOT / "frontend" / "src"

    for test_file in frontend_tests:
        matches = list(frontend_src.rglob(test_file))
        if not matches:
            missing.append(f"frontend/src/**/{test_file}")

    assert not missing, "Cited test files not found on disk:\n" + "\n".join(missing)
