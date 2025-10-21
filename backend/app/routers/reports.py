"""Reports endpoints for content moderation."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.core.auth import get_current_active_user, get_current_admin_user
from app.models.report import Report, ReportStatus, ReportType
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
    Create a new report for inappropriate content.
    
    Allows users to report decks or cards that violate community guidelines.
    
    Args:
        report_data: Report details (type, content_id, reason, description)
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        The created report
    """
    report = Report(
        reporter_id=current_user.id,
        report_type=report_data.report_type,
        content_id=report_data.content_id,
        reason=report_data.reason,
        description=report_data.description
    )
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return report


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    status_filter: Optional[ReportStatus] = None,
    report_type: Optional[ReportType] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all reports (admin only).
    
    Allows admins to view and filter reports for moderation.
    
    Args:
        status_filter: Optional filter by report status
        report_type: Optional filter by report type
        session: Database session
        current_user: Current admin user
        
    Returns:
        List of reports
    """
    statement = select(Report)
    
    if status_filter:
        statement = statement.where(Report.status == status_filter)
    if report_type:
        statement = statement.where(Report.report_type == report_type)
    
    reports = session.exec(statement).all()
    return reports


@router.get("/my-reports", response_model=List[ReportResponse])
async def get_my_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get reports created by the current user.
    
    Args:
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        List of user's reports
    """
    statement = select(Report).where(Report.reporter_id == current_user.id)
    reports = session.exec(statement).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific report by ID (admin only).
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Current admin user
        
    Returns:
        The report details
        
    Raises:
        HTTPException 404: If report not found
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a report status (admin only).
    
    Allows admins to mark reports as reviewed, resolved, or dismissed.
    
    Args:
        report_id: Report ID
        report_data: Updated status and admin notes
        session: Database session
        current_user: Current admin user
        
    Returns:
        The updated report
        
    Raises:
        HTTPException 404: If report not found
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.status = report_data.status
    report.reviewed_by = current_user.id
    if report_data.admin_notes:
        report.admin_notes = report_data.admin_notes
    report.updated_at = datetime.utcnow()
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a report (admin only).
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Current admin user
        
    Raises:
        HTTPException 404: If report not found
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    session.delete(report)
    session.commit()
    return None
