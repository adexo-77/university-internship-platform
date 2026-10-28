"""Domain service implementing student profile retrieval and updates."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.student_profile import StudentProfileUpdateRequest


class StudentProfileService:
    """Student profile business logic."""

    @staticmethod
    def get_profile(db: Session, user: User) -> StudentProfile:
        """Retrieve student profile for the authenticated user, creating if missing."""
        profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
        if profile is None:
            profile = StudentProfile(user_id=user.id, skills=[], preferred_work_modes=[])
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
        update_data: StudentProfileUpdateRequest,
    ) -> StudentProfile:
        """Update student profile details for the authenticated user."""
        profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
        if profile is None:
            profile = StudentProfile(user_id=user.id, skills=[], preferred_work_modes=[])
            db.add(profile)

        profile.university = update_data.university
        profile.department = update_data.department
        profile.year_of_study = update_data.year_of_study
        profile.bio = update_data.bio
        profile.skills = update_data.skills
        profile.preferred_work_modes = update_data.preferred_work_modes
        profile.preferred_location = update_data.preferred_location

        db.commit()
        db.refresh(profile)
        return profile
