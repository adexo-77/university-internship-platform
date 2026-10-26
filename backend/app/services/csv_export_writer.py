"""Safe CSV response builder with formula-injection mitigation, UTF-8 BOM, and limits."""

import csv
import io

from fastapi import Response

INJECTION_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
MAX_CSV_ROWS = 10000


def sanitize_csv_cell(value: object) -> str:
    """Neutralize formula injection by prepending apostrophe if cell starts with dangerous chars."""
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in INJECTION_PREFIXES:
        return f"'{text}"
    return text


def build_csv_response(
    headers: list[str],
    rows: list[list[object]],
    filename: str,
) -> Response:
    """Write sanitized rows with UTF-8 BOM, row cap, and no-store attachment headers."""
    stream = io.StringIO()
    stream.write("\ufeff")  # UTF-8 BOM for Microsoft Excel compatibility
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow([sanitize_csv_cell(h) for h in headers])

    for row in rows[:MAX_CSV_ROWS]:
        writer.writerow([sanitize_csv_cell(cell) for cell in row])

    return Response(
        content=stream.getvalue().encode("utf-8"),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
