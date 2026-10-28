"""Test asserting all image paths referenced in README.md and documentation exist on disk."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATHS = [REPO_ROOT / "README.md", REPO_ROOT / "CHANGELOG.md", REPO_ROOT / "AGENTS.md"]
DOC_PATHS.extend(REPO_ROOT.glob("docs/**/*.md"))

MD_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((.*?)\)")
HTML_IMAGE_PATTERN = re.compile(r"""<img[^>]+src=["']([^"']+)["']""")


def _extract_image_references(markdown_text: str) -> list[str]:
    """Extract local image URLs from markdown text."""
    raw_targets = MD_IMAGE_PATTERN.findall(markdown_text) + HTML_IMAGE_PATTERN.findall(
        markdown_text
    )
    local_images = []
    for target in raw_targets:
        clean = target.strip().split("#")[0].split("?")[0].strip()
        if not clean or clean.startswith(("http://", "https://", "data:")):
            continue
        local_images.append(clean)
    return local_images


def _check_doc_images(doc_file: Path) -> list[str]:
    """Return list of missing image errors for a given doc file."""
    if not doc_file.is_file():
        return []
    content = doc_file.read_text(encoding="utf-8")
    images = _extract_image_references(content)
    missing = []
    for img in images:
        rel_to_doc = doc_file.parent / img
        rel_to_root = REPO_ROOT / img
        if not (rel_to_doc.is_file() or rel_to_root.is_file()):
            missing.append(f"{doc_file.name}: image '{img}' not found on disk")
    return missing


def test_all_markdown_image_references_exist_on_disk() -> None:
    """Verify that every local image referenced across all docs exists on disk."""
    all_missing = []
    checked_images_count = 0

    for doc_file in DOC_PATHS:
        if not doc_file.is_file():
            continue
        content = doc_file.read_text(encoding="utf-8")
        images = _extract_image_references(content)
        checked_images_count += len(images)
        missing = _check_doc_images(doc_file)
        all_missing.extend(missing)

    assert not all_missing, f"Missing referenced images found: {all_missing}"
    assert checked_images_count > 0, "Expected to find and verify markdown image references"


def test_check_doc_images_fails_on_missing_reference(tmp_path: Path) -> None:
    """Verify that _check_doc_images detects a broken image link."""
    fake_doc = tmp_path / "test.md"
    fake_doc.write_text("![Broken](non_existent_screenshot.png)", encoding="utf-8")
    missing = _check_doc_images(fake_doc)
    assert len(missing) == 1
    assert "non_existent_screenshot.png" in missing[0]
