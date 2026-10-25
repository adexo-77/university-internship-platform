"""Database models package."""

from app.models.application import Application, ApplicationStatus
from app.models.assignment import Assignment
from app.models.base import Base
from app.models.course import Course, CourseStatus
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.notification import Notification, NotificationKind
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.session import Session
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User, UserRole

__all__ = [
    "Application",
    "ApplicationStatus",
    "ApprovalStatus",
    "Assignment",
    "Base",
    "Course",
    "CourseResource",
    "CourseStatus",
    "Enrollment",
    "Internship",
    "InternshipStatus",
    "InternshipWorkMode",
    "Notification",
    "NotificationKind",
    "OrganizationProfile",
    "Session",
    "StudentProfile",
    "Submission",
    "User",
    "UserRole",
]
