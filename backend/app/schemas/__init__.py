"""Pydantic schemas for request/response validation."""

from .auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenData,
    UserResponse,
)
from .deck import (
    DeckCreate,
    DeckUpdate,
    DeckResponse,
)
from .card import (
    CardCreate,
    CardUpdate,
    CardResponse,
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenData",
    "UserResponse",
    # Deck schemas
    "DeckCreate",
    "DeckUpdate",
    "DeckResponse",
    # Card schemas
    "CardCreate",
    "CardUpdate",
    "CardResponse",
]
