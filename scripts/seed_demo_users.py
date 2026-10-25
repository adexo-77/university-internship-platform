"""User and profile demo seed helpers for realistic demo roster."""

from datetime import UTC, datetime, timedelta

from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from sqlalchemy import select
from sqlalchemy.orm import Session

ROSTER_USERS = [
    ("mulugeta.assefa@example.com", "Dr. Mulugeta Assefa", UserRole.ADMIN),
    ("selamawit.tadesse@example.com", "Ms. Selamawit Tadesse", UserRole.COORDINATOR),
    ("tadesse.bekele@example.com", "Dr. Tadesse Bekele", UserRole.INSTRUCTOR),
    ("hana.worku@example.com", "Ms. Hana Worku", UserRole.INSTRUCTOR),
    ("abel.tesfaye@example.com", "Abel Tesfaye", UserRole.STUDENT),
    ("meron.girma@example.com", "Meron Girma", UserRole.STUDENT),
    ("dawit.lemma@example.com", "Dawit Lemma", UserRole.STUDENT),
    ("yohannes.haile@example.com", "Yohannes Haile", UserRole.ORGANIZATION),
    ("rahel.desta@example.com", "Rahel Desta", UserRole.ORGANIZATION),
    ("eyob.kassa@example.com", "Eyob Kassa", UserRole.ORGANIZATION),
]


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


def _seed_student_profiles(db: Session, s1: User, s2: User, s3: User) -> None:
    if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == s1.id)):
        db.add(
            StudentProfile(
                user_id=s1.id,
                university="Jimma University",
                department="Information Technology",
                year_of_study=4,
                skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Git"],
                bio="Final-year Information Technology student at Jimma University focused on full-stack web development and API engineering.",
            )
        )
    if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == s2.id)):
        db.add(
            StudentProfile(
                user_id=s2.id,
                university="Jimma University",
                department="Information Technology",
                year_of_study=3,
                skills=["Python", "TypeScript", "React", "Tailwind CSS", "SQL"],
                bio="Third-year IT undergraduate passionate about front-end architecture, UI/UX systems, and modern web application development.",
            )
        )
    if not db.scalar(select(StudentProfile).where(StudentProfile.user_id == s3.id)):
        db.add(StudentProfile(user_id=s3.id, skills=[]))


def _seed_organization_profiles(
    db: Session, admin: User, org1: User, org2: User, org3: User
) -> None:
    now = datetime.now(UTC)
    if not db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org1.id)
    ):
        db.add(
            OrganizationProfile(
                user_id=org1.id,
                organization_name="Kaffa Digital Solutions",
                industry="Software & Digital Solutions",
                website="https://kaffadigital.example.org",
                location="Addis Ababa",
                description="Enterprise cloud systems, banking platforms, and bespoke software across East Africa.",
                approval_status=ApprovalStatus.APPROVED,
                approval_note="Verified enterprise corporate partner.",
                reviewed_by=admin.id,
                reviewed_at=now - timedelta(days=60),
            )
        )
    if not db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org2.id)
    ):
        db.add(
            OrganizationProfile(
                user_id=org2.id,
                organization_name="Gibe Valley Telecom Services",
                industry="Telecommunications & Networking",
                website="https://gibevalleytelecom.example.org",
                location="Jimma",
                description="Regional broadband connectivity, optical network operations, and telecom infrastructure.",
                approval_status=ApprovalStatus.APPROVED,
                approval_note="Verified telecommunications service provider.",
                reviewed_by=admin.id,
                reviewed_at=now - timedelta(days=45),
            )
        )
    if not db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org3.id)
    ):
        db.add(
            OrganizationProfile(
                user_id=org3.id,
                organization_name="Abay Data Labs",
                industry="Data Analytics & AI",
                website="https://abaydatalabs.example.org",
                location="Addis Ababa",
                description="Specializing in statistical data engineering, machine learning pipelines, and business intelligence.",
                approval_status=ApprovalStatus.PENDING,
            )
        )


def seed_demo_users_and_profiles(db: Session, pw_hash: str) -> dict[str, User]:
    users: dict[str, User] = {}
    for email, name, role in ROSTER_USERS:
        users[email] = get_or_create_user(db, email, name, role, pw_hash)

    admin = users["mulugeta.assefa@example.com"]
    coord = users["selamawit.tadesse@example.com"]
    inst1 = users["tadesse.bekele@example.com"]
    inst2 = users["hana.worku@example.com"]
    s1 = users["abel.tesfaye@example.com"]
    s2 = users["meron.girma@example.com"]
    s3 = users["dawit.lemma@example.com"]
    org1 = users["yohannes.haile@example.com"]
    org2 = users["rahel.desta@example.com"]
    org3 = users["eyob.kassa@example.com"]

    _seed_student_profiles(db, s1, s2, s3)
    _seed_organization_profiles(db, admin, org1, org2, org3)
    db.flush()

    return {
        "admin": admin,
        "coord": coord,
        "coordinator": coord,
        "inst": inst1,
        "inst1": inst1,
        "inst2": inst2,
        "s1": s1,
        "s2": s2,
        "s3": s3,
        "org": org1,
        "org1": org1,
        "org2": org2,
        "org3": org3,
        "neworg": org3,
    }
