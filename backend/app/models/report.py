"""Report model for content moderation."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Types of content that can be reported."""
    DECK = "deck"
    CARD = "card"


class ReportReason(str, Enum):
    """Reasons for reporting content."""
    INAPPROPRIATE = "inappropriate"
    SPAM = "spam"
    COPYRIGHT = "copyright"
    MISLEADING = "misleading"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Status of a report."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Report(SQLModel, table=True):
    """Report model for user-reported content."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    reporter_id: int = Field(foreign_key="user.id", index=True)
    report_type: ReportType = Field(index=True)
    content_id: int = Field(index=True)  # ID of the deck or card being reported
    reason: ReportReason = Field(index=True)
    description: Optional[str] = None
    status: ReportStatus = Field(default=ReportStatus.PENDING, index=True)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
