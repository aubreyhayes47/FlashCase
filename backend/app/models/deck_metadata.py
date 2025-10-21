from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class DeckMetadata(SQLModel, table=True):
    """DeckMetadata model for tracking deck statistics and usage."""
    
    __tablename__ = "deck_metadata"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id", unique=True, index=True)
    card_count: int = Field(default=0)
    total_reviews: int = Field(default=0)
    average_rating: Optional[float] = Field(default=None)
    last_studied: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
