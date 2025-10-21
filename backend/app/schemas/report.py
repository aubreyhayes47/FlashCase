"""Report-related Pydantic schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.report import ReportType, ReportStatus, ReportReason


class ReportCreate(BaseModel):
    """Schema for creating a new report."""
    report_type: ReportType = Field(..., description="Type of content being reported")
    content_id: int = Field(..., description="ID of the content being reported")
    reason: ReportReason = Field(..., description="Reason for reporting")
    description: Optional[str] = Field(None, max_length=1000, description="Additional details about the report")


class ReportUpdate(BaseModel):
    """Schema for updating a report (admin only)."""
    status: Optional[ReportStatus] = Field(None, description="Report status")
    admin_notes: Optional[str] = Field(None, max_length=2000, description="Admin notes")


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: int = Field(..., description="Report ID")
    reporter_id: int = Field(..., description="ID of user who reported")
    report_type: ReportType = Field(..., description="Type of content reported")
    content_id: int = Field(..., description="ID of reported content")
    reason: ReportReason = Field(..., description="Reason for report")
    description: Optional[str] = Field(None, description="Report description")
    status: ReportStatus = Field(..., description="Current status")
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    reviewed_by: Optional[int] = Field(None, description="Admin who reviewed")
    reviewed_at: Optional[datetime] = Field(None, description="When reviewed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
