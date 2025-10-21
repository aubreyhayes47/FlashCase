"""Study session and review endpoints for spaced repetition."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, and_, or_
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_session
from app.models.card import Card
from app.models.study_log import StudyLog
from app.services.srs import calculate_sm2, calculate_due_date

router = APIRouter(prefix="/study", tags=["study"])


class CardWithStudyInfo(BaseModel):
    """Card with study information."""
    id: int
    deck_id: int
    front: str
    back: str
    ease_factor: float
    interval: int
    repetitions: int
    due_date: datetime
    
    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    """Request body for reviewing a card."""
    user_id: int
    quality: int  # 0-5 rating


class ReviewResponse(BaseModel):
    """Response after reviewing a card."""
    card_id: int
    quality: int
    new_ease_factor: float
    new_interval: int
    new_repetitions: int
    next_due_date: datetime


@router.get("/session/{deck_id}", response_model=List[CardWithStudyInfo])
async def get_study_session(
    deck_id: int,
    user_id: int,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """
    Get cards due for review in a specific deck for a user.
    
    Args:
        deck_id: The deck ID to get cards from
        user_id: The user ID to get cards for
        limit: Maximum number of cards to return (default 20)
        session: Database session
        
    Returns:
        List of cards with their study information, ordered by due date
        
    Algorithm:
        1. Get all cards in the deck
        2. For each card, get the latest study log for the user
        3. If no study log exists, create initial study info (new card)
        4. Filter for cards where due_date <= now
        5. Order by due_date (oldest first)
        6. Limit results
    """
    # Get all cards in the deck
    cards_stmt = select(Card).where(Card.deck_id == deck_id)
    cards = session.exec(cards_stmt).all()
    
    if not cards:
        return []
    
    due_cards = []
    now = datetime.utcnow()
    
    for card in cards:
        # Get the most recent study log for this card and user
        study_log_stmt = (
            select(StudyLog)
            .where(StudyLog.card_id == card.id)
            .where(StudyLog.user_id == user_id)
            .order_by(StudyLog.reviewed_at.desc())
        )
        study_log = session.exec(study_log_stmt).first()
        
        if study_log is None:
            # New card - not studied yet
            card_info = CardWithStudyInfo(
                id=card.id,
                deck_id=card.deck_id,
                front=card.front,
                back=card.back,
                ease_factor=2.5,
                interval=0,
                repetitions=0,
                due_date=now  # Due immediately
            )
            due_cards.append(card_info)
        elif study_log.due_date <= now:
            # Card is due for review
            card_info = CardWithStudyInfo(
                id=card.id,
                deck_id=card.deck_id,
                front=card.front,
                back=card.back,
                ease_factor=study_log.ease_factor,
                interval=study_log.interval,
                repetitions=study_log.repetitions,
                due_date=study_log.due_date
            )
            due_cards.append(card_info)
    
    # Sort by due date (oldest first) and limit
    due_cards.sort(key=lambda x: x.due_date)
    return due_cards[:limit]


@router.post("/review/{card_id}", response_model=ReviewResponse)
async def review_card(
    card_id: int,
    review: ReviewRequest,
    session: Session = Depends(get_session)
):
    """
    Submit a review for a card and update the study log using SM-2 algorithm.
    
    Args:
        card_id: The card ID being reviewed
        review: Review request containing user_id and quality rating (0-5)
        session: Database session
        
    Returns:
        ReviewResponse with updated study parameters
        
    Algorithm:
        1. Validate the card exists
        2. Get the most recent study log for this card/user
        3. Calculate new parameters using SM-2 algorithm
        4. Create a new study log entry with updated parameters
        5. Return the new study parameters
    """
    # Validate quality rating
    if not 0 <= review.quality <= 5:
        raise HTTPException(
            status_code=400,
            detail="Quality must be between 0 and 5"
        )
    
    # Verify card exists
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Get the most recent study log for this card and user
    study_log_stmt = (
        select(StudyLog)
        .where(StudyLog.card_id == card_id)
        .where(StudyLog.user_id == review.user_id)
        .order_by(StudyLog.reviewed_at.desc())
    )
    previous_log = session.exec(study_log_stmt).first()
    
    # Get current parameters or use defaults for new cards
    if previous_log:
        current_repetitions = previous_log.repetitions
        current_ease_factor = previous_log.ease_factor
        current_interval = previous_log.interval
    else:
        # New card - use defaults
        current_repetitions = 0
        current_ease_factor = 2.5
        current_interval = 0
    
    # Calculate new parameters using SM-2 algorithm
    new_repetitions, new_ease_factor, new_interval = calculate_sm2(
        quality=review.quality,
        repetitions=current_repetitions,
        ease_factor=current_ease_factor,
        interval=current_interval
    )
    
    # Calculate next due date
    next_due_date = calculate_due_date(new_interval)
    
    # Create new study log entry
    now = datetime.utcnow()
    new_study_log = StudyLog(
        user_id=review.user_id,
        card_id=card_id,
        reviewed_at=now,
        ease_factor=new_ease_factor,
        interval=new_interval,
        repetitions=new_repetitions,
        last_rating=review.quality,
        due_date=next_due_date,
        next_review=next_due_date,
        created_at=now
    )
    
    session.add(new_study_log)
    session.commit()
    session.refresh(new_study_log)
    
    return ReviewResponse(
        card_id=card_id,
        quality=review.quality,
        new_ease_factor=new_ease_factor,
        new_interval=new_interval,
        new_repetitions=new_repetitions,
        next_due_date=next_due_date
    )
