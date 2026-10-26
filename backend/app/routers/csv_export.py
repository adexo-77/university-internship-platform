"""Thin router for CSV export endpoints."""

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services import csv_export as csv_export_service

router = APIRouter(tags=["reports"])


@router.get(
    "/courses/{id}/gradebook.csv",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export course gradebook as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Safe CSV export of course gradebook.",
        }
    },
)
def export_course_gradebook(
    id: int = Path(..., description="Course ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Export student grades for a course as a UTF-8 CSV with BOM."""
    return csv_export_service.export_course_gradebook_csv(
        db=db,
        course_id=id,
        current_user=current_user,
    )


@router.get(
    "/internships/{id}/applicants.csv",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export internship applicants as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Safe CSV export of applicants roster.",
        }
    },
)
def export_internship_applicants(
    id: int = Path(..., description="Internship ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Export applicants for an internship posting as a UTF-8 CSV with BOM."""
    return csv_export_service.export_internship_applicants_csv(
        db=db,
        internship_id=id,
        current_user=current_user,
    )


@router.get(
    "/admin/reports/applications.csv",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export all applications report as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Safe CSV export of platform applications.",
        }
    },
)
def export_applications_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Export platform applications as a UTF-8 CSV with BOM for admin and coordinator."""
    return csv_export_service.export_applications_report_csv(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/admin/reports/users.csv",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export all users report as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Safe CSV export of platform users.",
        }
    },
)
def export_users_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Export platform users as a UTF-8 CSV with BOM for admin only."""
    return csv_export_service.export_users_report_csv(
        db=db,
        current_user=current_user,
    )
