"""Card-related Pydantic schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CardCreate(BaseModel):
    """Schema for creating a new card."""
    deck_id: int = Field(..., description="Deck ID that this card belongs to")
    front: str = Field(..., min_length=1, max_length=2000, description="Front of the card (question)")
    back: str = Field(..., min_length=1, max_length=5000, description="Back of the card (answer)")


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    front: Optional[str] = Field(None, min_length=1, max_length=2000, description="Front of the card (question)")
    back: Optional[str] = Field(None, min_length=1, max_length=5000, description="Back of the card (answer)")


class CardResponse(BaseModel):
    """Schema for card response."""
    id: int = Field(..., description="Card ID")
    deck_id: int = Field(..., description="Deck ID")
    front: str = Field(..., description="Front of the card (question)")
    back: str = Field(..., description="Back of the card (answer)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
