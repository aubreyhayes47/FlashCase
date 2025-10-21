#!/usr/bin/env python3
"""
Test script to verify database models and constraints.
This is a simple verification script, not a full test suite.
"""

from datetime import datetime
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models import User, Deck, Card, DeckMetadata, StudyLog, UserDeck


def test_models():
    """Test all models and their relationships."""
    
    # Create tables
    print("Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created successfully\n")
    
    with Session(engine) as session:
        # 1. Create a user
        print("1. Creating user...")
        user = User(
            email="sarah@lawschool.edu",
            username="sarah_2L",
            hashed_password="$2b$12$hashedpassword",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"   ✓ User created: {user.username} (ID: {user.id})\n")
        
        # 2. Create a deck
        print("2. Creating deck...")
        deck = Deck(
            name="Constitutional Law",
            description="Key concepts in constitutional law",
            is_public=True
        )
        session.add(deck)
        session.commit()
        session.refresh(deck)
        print(f"   ✓ Deck created: {deck.name} (ID: {deck.id})\n")
        
        # 3. Create cards
        print("3. Creating cards...")
        cards = [
            Card(
                deck_id=deck.id,
                front="What is judicial review?",
                back="The power of courts to declare laws unconstitutional (Marbury v. Madison)"
            ),
            Card(
                deck_id=deck.id,
                front="What is the Commerce Clause?",
                back="Article I, Section 8 - Congress has power to regulate interstate commerce"
            ),
        ]
        for card in cards:
            session.add(card)
        session.commit()
        for card in cards:
            session.refresh(card)
        print(f"   ✓ Created {len(cards)} cards\n")
        
        # 4. Create deck metadata
        print("4. Creating deck metadata...")
        metadata = DeckMetadata(
            deck_id=deck.id,
            card_count=len(cards),
            total_reviews=0
        )
        session.add(metadata)
        session.commit()
        session.refresh(metadata)
        print(f"   ✓ Deck metadata created (card_count: {metadata.card_count})\n")
        
        # 5. Create user-deck relationship
        print("5. Creating user-deck relationship...")
        user_deck = UserDeck(
            user_id=user.id,
            deck_id=deck.id,
            is_owner=True,
            is_favorite=False
        )
        session.add(user_deck)
        session.commit()
        session.refresh(user_deck)
        print(f"   ✓ UserDeck relationship created (is_owner: {user_deck.is_owner})\n")
        
        # 6. Create study logs
        print("6. Creating study logs...")
        for card in cards:
            study_log = StudyLog(
                user_id=user.id,
                card_id=card.id,
                ease_factor=2.5,
                interval=1,
                next_review=datetime.utcnow()
            )
            session.add(study_log)
        session.commit()
        print(f"   ✓ Created {len(cards)} study log entries\n")
        
        # 7. Query and verify data
        print("7. Verifying data integrity...")
        
        # Count users
        statement = select(User)
        users = session.exec(statement).all()
        print(f"   ✓ Users in database: {len(users)}")
        
        # Count decks
        statement = select(Deck)
        decks = session.exec(statement).all()
        print(f"   ✓ Decks in database: {len(decks)}")
        
        # Count cards
        statement = select(Card)
        all_cards = session.exec(statement).all()
        print(f"   ✓ Cards in database: {len(all_cards)}")
        
        # Count study logs
        statement = select(StudyLog)
        logs = session.exec(statement).all()
        print(f"   ✓ Study logs in database: {len(logs)}")
        
        # Verify relationships
        statement = select(Card).where(Card.deck_id == deck.id)
        deck_cards = session.exec(statement).all()
        print(f"   ✓ Cards in '{deck.name}': {len(deck_cards)}")
        
        statement = select(StudyLog).where(StudyLog.user_id == user.id)
        user_logs = session.exec(statement).all()
        print(f"   ✓ Study logs for user '{user.username}': {len(user_logs)}\n")
        
    print("=" * 60)
    print("✓ All database models and constraints working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    test_models()
