from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.deck import Deck

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=List[Deck])
async def list_decks(session: Session = Depends(get_session)):
    """List all decks."""
    statement = select(Deck)
    decks = session.exec(statement).all()
    return decks


@router.get("/{deck_id}", response_model=Deck)
async def get_deck(deck_id: int, session: Session = Depends(get_session)):
    """Get a specific deck."""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@router.post("/", response_model=Deck)
async def create_deck(deck: Deck, session: Session = Depends(get_session)):
    """Create a new deck."""
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.delete("/{deck_id}")
async def delete_deck(deck_id: int, session: Session = Depends(get_session)):
    """Delete a deck."""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    session.delete(deck)
    session.commit()
    return {"message": "Deck deleted successfully"}
