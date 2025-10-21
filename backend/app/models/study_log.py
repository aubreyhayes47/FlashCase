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
    ease_factor: float = Field(default=2.5)  # Used in spaced repetition algorithm (EF, floor 1.3)
    interval: int = Field(default=0)  # Days until next review
    repetitions: int = Field(default=0)  # Number of consecutive correct repetitions
    last_rating: Optional[int] = Field(default=None)  # Last quality rating (0-5 in SM-2)
    due_date: datetime = Field(default_factory=datetime.utcnow, index=True)  # When card is due for review
    next_review: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
