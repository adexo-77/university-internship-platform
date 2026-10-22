"""Input sanitization and validation helpers to protect against malformed data."""

import unicodedata


def clean_text(
    value: str,
    field_name: str = "Field",
    max_length: int = 255,
    allow_newlines: bool = False,
) -> str:
    """Validate that text contains no null bytes or forbidden control characters."""
    if "\x00" in value:
        raise ValueError(f"{field_name} cannot contain null bytes.")

    for ch in value:
        code = ord(ch)
        if code < 32 or code == 127:
            if allow_newlines and ch in ("\n", "\r", "\t"):
                continue
            raise ValueError(f"{field_name} cannot contain control characters.")

    trimmed = value.strip()
    if len(trimmed) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters.")
    return trimmed


def clean_optional_text(
    value: str | None,
    field_name: str = "Field",
    max_length: int = 255,
    allow_newlines: bool = False,
) -> str | None:
    """Sanitize optional text fields, normalizing blank to None."""
    if value is None:
        return None
    cleaned = clean_text(
        value=value,
        field_name=field_name,
        max_length=max_length,
        allow_newlines=allow_newlines,
    )
    return cleaned if cleaned else None


def normalize_email(raw_email: str) -> str:
    """Safely normalize unicode email using NFKC and reject null bytes and control chars."""
    if "\x00" in raw_email:
        raise ValueError("Email address cannot contain null bytes.")

    for ch in raw_email:
        if ord(ch) < 32 or ord(ch) == 127:
            raise ValueError("Email address cannot contain control characters.")

    normalized = unicodedata.normalize("NFKC", raw_email).strip().lower()
    if not normalized or len(normalized) > 255 or "@" not in normalized:
        raise ValueError("A valid email address is required.")

    parts = normalized.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1] or "." not in parts[1]:
        raise ValueError("A valid email address is required.")

    return normalized
