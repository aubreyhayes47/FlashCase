"""Report endpoints for content moderation."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.core.database import get_session
from app.core.auth import get_current_active_user
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new content report.
    
    Users can report decks, cards, or other users for inappropriate content,
    spam, harassment, or other violations.
    
    Args:
        report_data: Report details
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        The created report
    """
    # Create the report
    report = Report(
        reporter_id=current_user.id,
        report_type=report_data.report_type,
        content_id=report_data.content_id,
        reason=report_data.reason,
        description=report_data.description,
        status=ReportStatus.PENDING
    )
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return report


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    status_filter: ReportStatus = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List reports created by the current user.
    
    Users can only see their own reports. Admins would need a separate
    endpoint to view all reports (to be implemented).
    
    Args:
        status_filter: Optional filter by report status
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        List of user's reports
    """
    statement = select(Report).where(Report.reporter_id == current_user.id)
    
    if status_filter:
        statement = statement.where(Report.status == status_filter)
    
    reports = session.exec(statement).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific report.
    
    Users can only view their own reports.
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        Report details
        
    Raises:
        HTTPException 404: If report not found
        HTTPException 403: If user doesn't own the report
    """
    report = session.get(Report, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Users can only view their own reports
    if report.reporter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )
    
    return report


# Admin endpoints would go here (not implemented in MVP)
# Example: GET /reports/admin/all - List all reports for admin review
# Example: PATCH /reports/admin/{report_id} - Update report status
