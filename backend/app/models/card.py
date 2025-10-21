from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Card(SQLModel, table=True):
    """Card model for flashcards."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id", index=True)
    front: str
    back: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
