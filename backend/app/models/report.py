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
    USER = "user"


class ReportStatus(str, Enum):
    """Status of a report."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportReason(str, Enum):
    """Reasons for reporting content."""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SPAM = "spam"
    HARASSMENT = "harassment"
    INCORRECT_INFORMATION = "incorrect_information"
    COPYRIGHT_VIOLATION = "copyright_violation"
    OTHER = "other"


class Report(SQLModel, table=True):
    """Report model for flagging inappropriate content."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Reporter information
    reporter_id: int = Field(foreign_key="user.id", index=True)
    
    # What is being reported
    report_type: ReportType = Field(index=True)
    content_id: int = Field(index=True)  # ID of the deck, card, or user being reported
    
    # Report details
    reason: ReportReason = Field(index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Admin review
    status: ReportStatus = Field(default=ReportStatus.PENDING, index=True)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
