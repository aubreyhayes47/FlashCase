from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.core.auth import get_current_active_user
from app.models.card import Card
from app.models.deck import Deck
from app.models.user import User
from app.schemas.card import CardCreate, CardUpdate, CardResponse
from app.services.content_moderation import validate_card_content

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/", response_model=List[CardResponse])
async def list_cards(
    deck_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List cards, optionally filtered by deck.
    
    Args:
        deck_id: Optional deck ID to filter cards
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        List of cards
    """
    statement = select(Card)
    if deck_id:
        statement = statement.where(Card.deck_id == deck_id)
    cards = session.exec(statement).all()
    return cards


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific card by ID."""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new card in a deck with content moderation.
    
    Args:
        card_data: Card creation data (deck_id, front, back)
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        The created card
        
    Raises:
        HTTPException 404: If deck doesn't exist
        HTTPException 400: If content contains inappropriate language
    """
    # Verify deck exists
    deck = session.get(Deck, card_data.deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Validate content for inappropriate language
    is_valid, error_message = validate_card_content(card_data.front, card_data.back)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    card = Card(
        deck_id=card_data.deck_id,
        front=card_data.front,
        back=card_data.back
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing card with content moderation.
    
    Args:
        card_id: Card ID to update
        card_data: Card update data (front and/or back)
        session: Database session
        current_user: Currently authenticated user
        
    Returns:
        The updated card
        
    Raises:
        HTTPException 404: If card doesn't exist
        HTTPException 400: If content contains inappropriate language
    """
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    
    # Build updated values for validation
    updated_front = card_data.front if card_data.front is not None else card.front
    updated_back = card_data.back if card_data.back is not None else card.back
    
    # Validate content for inappropriate language
    is_valid, error_message = validate_card_content(updated_front, updated_back)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Update only provided fields
    if card_data.front is not None:
        card.front = card_data.front
    if card_data.back is not None:
        card.back = card_data.back
    
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a card."""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    session.delete(card)
    session.commit()
    return None
