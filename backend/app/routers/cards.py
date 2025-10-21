from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.card import Card

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/", response_model=List[Card])
async def list_cards(deck_id: int = None, session: Session = Depends(get_session)):
    """List cards, optionally filtered by deck."""
    statement = select(Card)
    if deck_id:
        statement = statement.where(Card.deck_id == deck_id)
    cards = session.exec(statement).all()
    return cards


@router.get("/{card_id}", response_model=Card)
async def get_card(card_id: int, session: Session = Depends(get_session)):
    """Get a specific card."""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post("/", response_model=Card)
async def create_card(card: Card, session: Session = Depends(get_session)):
    """Create a new card."""
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.delete("/{card_id}")
async def delete_card(card_id: int, session: Session = Depends(get_session)):
    """Delete a card."""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    session.delete(card)
    session.commit()
    return {"message": "Card deleted successfully"}
