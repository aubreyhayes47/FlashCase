from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Deck(SQLModel, table=True):
    """Deck model for organizing flashcards."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    # Metadata fields for discovery filtering
    school: Optional[str] = Field(default=None, index=True)
    course: Optional[str] = Field(default=None, index=True)
    professor: Optional[str] = Field(default=None, index=True)
    year: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
