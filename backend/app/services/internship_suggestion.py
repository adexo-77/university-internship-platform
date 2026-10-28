"""Deterministic scoring service and candidate retrieval for suggested internships."""

import enum
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.models.application import Application
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.internship_suggestion import (
    InternshipSuggestionItem,
    InternshipSuggestionReasons,
    InternshipSuggestionResponse,
)

# Named constants for scoring weights and thresholds
MAX_SKILL_POINTS: int = 60
POINTS_PER_SKILL: int = 12
MAX_COUNTED_SKILLS: int = 5

WORK_MODE_MAX_POINTS: int = 20
WORK_MODE_NEUTRAL_POINTS: int = 10

LOCATION_MAX_POINTS: int = 20
LOCATION_NEUTRAL_POINTS: int = 10

MIN_SUGGESTION_SCORE: int = 30
MAX_CANDIDATE_POSTINGS: int = 300


@dataclass(frozen=True)
class ScoredInternship:
    """Scored candidate posting with match breakdown."""

    posting: Internship
    org_name: str | None
    score: int
    matched_skills: list[str]
    work_mode_match: bool | None
    location_match: bool | None


def build_skill_pattern(skill: str) -> re.Pattern[str]:
    """Compile custom boundary regex ensuring whole-word/phrase matches for skills."""
    escaped = re.escape(skill.strip())
    pattern = rf"(?<![\w]){escaped}(?![\w#+])"
    return re.compile(pattern, re.IGNORECASE)


def score_posting(
    title: str,
    description: str,
    requirements: str,
    work_mode: str,
    location: str,
    student_skills: list[str],
    preferred_work_modes: list[str],
    preferred_location: str | None,
) -> tuple[int, list[str], bool | None, bool | None]:
    """Pure, deterministic scoring for an internship posting against student profile."""
    seen_lower: set[str] = set()
    distinct_skills: list[str] = []
    for s in student_skills:
        trimmed = s.strip()
        if not trimmed:
            continue
        lower = trimmed.lower()
        if lower not in seen_lower:
            seen_lower.add(lower)
            distinct_skills.append(trimmed)

    combined_text = f"{title} {description} {requirements}"
    matched_skills: list[str] = []
    for skill in distinct_skills:
        pattern = build_skill_pattern(skill)
        if pattern.search(combined_text):
            matched_skills.append(skill)

    skill_points = min(len(matched_skills), MAX_COUNTED_SKILLS) * POINTS_PER_SKILL

    norm_pref_modes = {m.strip().lower() for m in preferred_work_modes if m.strip()}
    posting_mode = work_mode.lower().strip()

    if not norm_pref_modes:
        work_mode_points = WORK_MODE_NEUTRAL_POINTS
        work_mode_match = None
    elif posting_mode in norm_pref_modes:
        work_mode_points = WORK_MODE_MAX_POINTS
        work_mode_match = True
    else:
        work_mode_points = 0
        work_mode_match = False

    clean_pref_loc = (
        preferred_location.strip().lower()
        if preferred_location and preferred_location.strip()
        else None
    )

    if posting_mode == "remote":
        location_points = LOCATION_MAX_POINTS
        location_match = True
    elif clean_pref_loc is None:
        location_points = LOCATION_NEUTRAL_POINTS
        location_match = None
    elif clean_pref_loc == location.strip().lower():
        location_points = LOCATION_MAX_POINTS
        location_match = True
    else:
        location_points = 0
        location_match = False

    total_score = skill_points + work_mode_points + location_points
    return total_score, matched_skills, work_mode_match, location_match


def get_candidate_postings(db: Session, student_id: int) -> list[tuple[Internship, str | None]]:
    """Fetch candidate postings with ONE query matching student catalogue visibility."""
    now = datetime.now(UTC)
    org_col = func.coalesce(OrganizationProfile.organization_name, User.full_name)

    stmt = (
        select(Internship, org_col.label("org_name"))
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(
            Internship.status == InternshipStatus.OPEN,
            Internship.application_deadline > now,
            User.is_active.is_(True),
            OrganizationProfile.approval_status == ApprovalStatus.APPROVED,
            Internship.id.not_in(
                select(Application.posting_id).where(Application.student_id == student_id)
            ),
        )
        .order_by(Internship.created_at.desc(), Internship.id.desc())
        .limit(MAX_CANDIDATE_POSTINGS)
    )
    return list(db.execute(stmt).all())


def get_internship_suggestions(
    db: Session,
    current_user: User,
    limit: int = 5,
) -> InternshipSuggestionResponse:
    """Retrieve scored and sorted internship suggestions for the authenticated student."""
    if current_user.role != UserRole.STUDENT:
        raise ForbiddenException(
            message="Only students can view suggested internships",
            code="FORBIDDEN",
        )

    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    if not profile or not profile.skills or not any(s.strip() for s in profile.skills):
        return InternshipSuggestionResponse(items=[], reason_code="NO_SKILLS")

    clamped_limit = min(max(limit, 1), 10)
    candidates = get_candidate_postings(db, current_user.id)

    scored: list[ScoredInternship] = []
    for posting, org_name in candidates:
        mode_str = (
            posting.work_mode.value
            if isinstance(posting.work_mode, enum.Enum)
            else str(posting.work_mode)
        )
        total_score, matched_skills, wm_match, loc_match = score_posting(
            title=posting.title,
            description=posting.description,
            requirements=posting.requirements,
            work_mode=mode_str,
            location=posting.location,
            student_skills=profile.skills,
            preferred_work_modes=profile.preferred_work_modes or [],
            preferred_location=profile.preferred_location,
        )
        if matched_skills and total_score >= MIN_SUGGESTION_SCORE:
            scored.append(
                ScoredInternship(
                    posting=posting,
                    org_name=org_name,
                    score=total_score,
                    matched_skills=matched_skills,
                    work_mode_match=wm_match,
                    location_match=loc_match,
                )
            )

    scored.sort(key=lambda s: (-s.score, s.posting.application_deadline, s.posting.id))
    top = scored[:clamped_limit]

    items = [
        InternshipSuggestionItem(
            id=s.posting.id,
            organization_id=s.posting.organization_id,
            organization_name=s.org_name,
            title=s.posting.title,
            description=s.posting.description,
            requirements=s.posting.requirements,
            location=s.posting.location,
            work_mode=s.posting.work_mode,
            duration_weeks=s.posting.duration_weeks,
            application_deadline=s.posting.application_deadline,
            status=s.posting.status,
            created_at=s.posting.created_at,
            updated_at=s.posting.updated_at,
            applicant_count=0,
            applications_accepted=True,
            applied=False,
            application_status=None,
            score=s.score,
            reasons=InternshipSuggestionReasons(
                matched_skills=s.matched_skills,
                work_mode_match=s.work_mode_match,
                location_match=s.location_match,
            ),
        )
        for s in top
    ]
    return InternshipSuggestionResponse(items=items, reason_code=None)
