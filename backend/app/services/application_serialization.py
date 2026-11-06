"""Helper functions for internship application serialization and profile resolution."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.application import ApplicantProfile, ApplicationResponse


def get_org_name(db: Session, org_id: int) -> str | None:
    """Resolve display organization name or user full name for an organization user."""
    return db.scalar(
        select(func.coalesce(OrganizationProfile.organization_name, User.full_name))
        .select_from(User)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(User.id == org_id)
    )


def to_applicant(u: User, p: StudentProfile | None) -> ApplicantProfile:
    """Format an applicant user and profile into ApplicantProfile schema."""
    return ApplicantProfile(
        user_id=u.id,
        full_name=u.full_name,
        email=u.email,
        university=p.university if p else None,
        department=p.department if p else None,
        year_of_study=p.year_of_study if p else None,
        skills=p.skills if p else [],
        bio=p.bio if p else None,
    )


def to_response(
    a: Application,
    posting_title: str | None = None,
    org_name: str | None = None,
    applicant: ApplicantProfile | None = None,
) -> ApplicationResponse:
    """Format Application model into ApplicationResponse schema."""
    res = ApplicationResponse.model_validate(a)
    res.posting_title = posting_title
    res.organization_name = org_name
    res.applicant = applicant
    return res
