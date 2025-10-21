from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class StudyLog(SQLModel, table=True):
    """StudyLog model for tracking study sessions and spaced repetition data."""
    
    __tablename__ = "study_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    card_id: int = Field(foreign_key="card.id", index=True)
    reviewed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    ease_factor: float = Field(default=2.5)  # Used in spaced repetition algorithm
    interval: int = Field(default=0)  # Days until next review
    next_review: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
