"""Report-related Pydantic schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.report import ReportType, ReportReason, ReportStatus


class ReportCreate(BaseModel):
    """Schema for creating a report."""
    report_type: ReportType = Field(..., description="Type of content being reported")
    content_id: int = Field(..., description="ID of the content being reported")
    reason: ReportReason = Field(..., description="Reason for reporting")
    description: Optional[str] = Field(None, max_length=500, description="Additional details (max 500 characters)")


class ReportUpdate(BaseModel):
    """Schema for updating a report (admin only)."""
    status: ReportStatus = Field(..., description="New status for the report")
    admin_notes: Optional[str] = Field(None, max_length=1000, description="Admin notes (max 1000 characters)")


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: int = Field(..., description="Report ID")
    reporter_id: int = Field(..., description="ID of user who made the report")
    report_type: ReportType = Field(..., description="Type of content reported")
    content_id: int = Field(..., description="ID of reported content")
    reason: ReportReason = Field(..., description="Reason for report")
    description: Optional[str] = Field(None, description="Additional details")
    status: ReportStatus = Field(..., description="Current status")
    reviewed_by: Optional[int] = Field(None, description="ID of admin who reviewed")
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    created_at: datetime = Field(..., description="Report creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
