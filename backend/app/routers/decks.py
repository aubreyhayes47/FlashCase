from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from app.core.database import get_session
from app.core.auth import get_current_active_user
from app.models.deck import Deck
from app.models.user import User
from app.schemas.deck import DeckCreate, DeckUpdate, DeckResponse
from app.services.content_moderation import validate_deck_content

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=List[DeckResponse])
async def list_decks(
    school: str = None,
    course: str = None,
    professor: str = None,
    year: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all decks accessible to the current user.
    
    Returns both user's own decks and public decks.
    Supports filtering by school, course, professor, and year.
    """
    statement = select(Deck)
    
    # Apply filters if provided
    if school:
        statement = statement.where(Deck.school == school)
    if course:
        statement = statement.where(Deck.course == course)
    if professor:
        statement = statement.where(Deck.professor == professor)
    if year:
        statement = statement.where(Deck.year == year)
    
    decks = session.exec(statement).all()
    return decks


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific deck by ID."""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck


@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new deck with content moderation."""
    # Validate content for inappropriate language
    is_valid, error_message = validate_deck_content(deck_data.name, deck_data.description)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    deck = Deck(
        name=deck_data.name,
        description=deck_data.description,
        is_public=deck_data.is_public,
        school=deck_data.school,
        course=deck_data.course,
        professor=deck_data.professor,
        year=deck_data.year
    )
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: int,
    deck_data: DeckUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing deck with content moderation."""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    
    # Build updated values for validation
    updated_name = deck_data.name if deck_data.name is not None else deck.name
    updated_description = deck_data.description if deck_data.description is not None else deck.description
    
    # Validate content for inappropriate language
    is_valid, error_message = validate_deck_content(updated_name, updated_description)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Update only provided fields
    if deck_data.name is not None:
        deck.name = deck_data.name
    if deck_data.description is not None:
        deck.description = deck_data.description
    if deck_data.is_public is not None:
        deck.is_public = deck_data.is_public
    if deck_data.school is not None:
        deck.school = deck_data.school
    if deck_data.course is not None:
        deck.course = deck_data.course
    if deck_data.professor is not None:
        deck.professor = deck_data.professor
    if deck_data.year is not None:
        deck.year = deck_data.year
    
    deck.updated_at = datetime.utcnow()
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a deck."""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    session.delete(deck)
    session.commit()
    return None
