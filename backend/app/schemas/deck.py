"""Deck-related Pydantic schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DeckCreate(BaseModel):
    """Schema for creating a new deck."""
    name: str = Field(..., min_length=1, max_length=200, description="Deck name")
    description: Optional[str] = Field(None, max_length=1000, description="Deck description")
    is_public: bool = Field(default=False, description="Whether deck is publicly visible")


class DeckUpdate(BaseModel):
    """Schema for updating a deck."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Deck name")
    description: Optional[str] = Field(None, max_length=1000, description="Deck description")
    is_public: Optional[bool] = Field(None, description="Whether deck is publicly visible")


class DeckResponse(BaseModel):
    """Schema for deck response."""
    id: int = Field(..., description="Deck ID")
    name: str = Field(..., description="Deck name")
    description: Optional[str] = Field(None, description="Deck description")
    is_public: bool = Field(..., description="Whether deck is publicly visible")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
