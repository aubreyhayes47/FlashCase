from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint
from typing import Optional
from datetime import datetime


class UserDeck(SQLModel, table=True):
    """UserDeck model for many-to-many relationship between users and decks."""
    
    __tablename__ = "user_deck"
    __table_args__ = (UniqueConstraint("user_id", "deck_id", name="unique_user_deck"),)
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    deck_id: int = Field(foreign_key="deck.id", index=True)
    is_owner: bool = Field(default=False)
    is_favorite: bool = Field(default=False)
    added_at: datetime = Field(default_factory=datetime.utcnow)
