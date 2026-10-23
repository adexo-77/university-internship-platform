"""User and profile demo seed helpers."""

from datetime import UTC, datetime, timedelta

from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_or_create_user(
    db: Session, email: str, full_name: str, role: UserRole, pw_hash: str
) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            role=role,
            password_hash=pw_hash,
            is_active=True,
        )
        db.add(user)
        db.flush()
    return user


def seed_demo_users_and_profiles(db: Session, pw_hash: str) -> dict[str, User]:
    admin = get_or_create_user(
        db, "demo.admin@example.com", "Demo Admin", UserRole.ADMIN, pw_hash
    )
    inst = get_or_create_user(
        db,
        "demo.instructor@example.com",
        "Demo Instructor",
        UserRole.INSTRUCTOR,
        pw_hash,
    )
    s1 = get_or_create_user(
        db, "demo.student@example.com", "Demo Student", UserRole.STUDENT, pw_hash
    )
    s2 = get_or_create_user(
        db, "demo.student2@example.com", "Demo Student Two", UserRole.STUDENT, pw_hash
    )
    org = get_or_create_user(
        db, "demo.org@example.com", "Demo Tech Corp", UserRole.ORGANIZATION, pw_hash
    )
    neworg = get_or_create_user(
        db,
        "demo.neworg@example.com",
        "Demo Innovations Ltd",
        UserRole.ORGANIZATION,
        pw_hash,
    )

    if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == s1.id)):
        db.add(
            StudentProfile(
                user_id=s1.id,
                university="State University",
                department="Computer Science",
                year_of_study=3,
                skills=["Python", "FastAPI", "React", "PostgreSQL"],
                bio="Passionate CS student seeking software engineering internships.",
            )
        )
    if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == s2.id)):
        db.add(StudentProfile(user_id=s2.id, skills=[]))

    if not db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org.id)
    ):
        db.add(
            OrganizationProfile(
                user_id=org.id,
                organization_name="Demo Tech Corp",
                industry="Software & Cloud",
                website="https://demotech.example.com",
                location="San Francisco, CA",
                description="Building next-generation distributed systems and web platforms.",
                approval_status=ApprovalStatus.APPROVED,
                approval_note="Verified registered enterprise.",
                reviewed_by=admin.id,
                reviewed_at=datetime.now(UTC) - timedelta(days=60),
            )
        )
    if not db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == neworg.id)
    ):
        db.add(
            OrganizationProfile(
                user_id=neworg.id,
                organization_name="Demo Innovations Ltd",
                industry="Healthcare Tech",
                website="https://demoinnovations.example.com",
                location="Boston, MA",
                description="Innovating modern patient analytics platforms.",
                approval_status=ApprovalStatus.PENDING,
            )
        )
    db.flush()
    return {
        "admin": admin,
        "inst": inst,
        "s1": s1,
        "s2": s2,
        "org": org,
        "neworg": neworg,
    }
