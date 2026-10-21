"""Application deadline validation and cap enforcement rules for internship postings."""

from datetime import UTC, datetime, timedelta

from app.core.exceptions import ConflictException
from app.models.internship import Internship, InternshipStatus
from app.schemas.internship import InternshipResponse

MAX_DEADLINE_DAYS = 90


def ensure_utc(dt: datetime) -> datetime:
    """Normalize datetime to UTC timezone."""
    return dt.astimezone(UTC) if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def check_deadline_cap(deadline: datetime, p: Internship | None = None) -> None:
    """Enforce maximum deadline cap relative to review time or current time."""
    dl = ensure_utc(deadline)
    ref = (
        ensure_utc(p.reviewed_at)
        if p and p.status == InternshipStatus.OPEN and p.reviewed_at
        else datetime.now(UTC)
    )
    max_dl = ref + timedelta(days=MAX_DEADLINE_DAYS)
    if dl > max_dl:
        max_str = max_dl.strftime("%d %b %Y")
        raise ConflictException(
            message=f"Application deadline cannot be later than {max_str}",
            code="DEADLINE_CAP_EXCEEDED",
        )


def update_posting_deadline(p: Internship, new_deadline: datetime) -> None:
    """Validate and apply a new application deadline based on posting status."""
    if p.status == InternshipStatus.OPEN:
        new_dl = ensure_utc(new_deadline)
        cur_dl = ensure_utc(p.application_deadline)
        if new_dl <= cur_dl:
            raise ConflictException(
                message="Application deadline can only be extended, not shortened",
                code="DEADLINE_CANNOT_BE_SHORTENED",
            )
        check_deadline_cap(new_dl, p)
        p.application_deadline = new_dl
    else:
        check_deadline_cap(new_deadline, p)
        p.application_deadline = new_deadline


def is_applications_accepted(p: Internship, current_time: datetime | None = None) -> bool:
    """Return True if posting is open and deadline is in the future."""
    now = current_time or datetime.now(UTC)
    return p.status == InternshipStatus.OPEN and p.application_deadline > now


def to_internship_response(
    p: Internship,
    org_name: str | None,
    applicant_count: int = 0,
    now: datetime | None = None,
    include_review: bool = False,
) -> InternshipResponse:
    """Serialize an Internship model to InternshipResponse schema."""
    current_time = now or datetime.now(UTC)
    return InternshipResponse(
        id=p.id,
        organization_id=p.organization_id,
        organization_name=org_name,
        title=p.title,
        description=p.description,
        requirements=p.requirements,
        location=p.location,
        work_mode=p.work_mode,
        duration_weeks=p.duration_weeks,
        application_deadline=p.application_deadline,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        applicant_count=applicant_count,
        applications_accepted=is_applications_accepted(p, current_time),
        review_note=p.review_note if include_review else None,
        reviewed_at=p.reviewed_at if include_review else None,
        reviewed_by=p.reviewed_by if include_review else None,
    )
