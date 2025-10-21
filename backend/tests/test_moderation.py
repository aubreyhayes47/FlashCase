"""Tests for content moderation features."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.services.moderation import (
    ProfanityFilter, 
    check_deck_content, 
    check_card_content
)


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient):
    """Create a user and return auth token."""
    # Register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


class TestProfanityFilter:
    """Test the profanity filter functionality."""
    
    def test_clean_text(self):
        """Test that clean text passes the filter."""
        filter = ProfanityFilter()
        assert filter.contains_profanity("This is a clean sentence") is False
        assert filter.contains_profanity("Contract Law Case Study") is False
        assert filter.contains_profanity("Torts and Constitutional Law") is False
    
    def test_profanity_detection(self):
        """Test that profanity is detected."""
        filter = ProfanityFilter()
        assert filter.contains_profanity("This is fucking bad") is True
        assert filter.contains_profanity("This shit won't work") is True
        assert filter.contains_profanity("You're a damn idiot") is True
    
    def test_case_insensitive(self):
        """Test that profanity detection is case-insensitive."""
        filter = ProfanityFilter()
        assert filter.contains_profanity("FUCK THIS") is True
        assert filter.contains_profanity("Fuck This") is True
        assert filter.contains_profanity("fuck this") is True
    
    def test_word_boundaries(self):
        """Test that profanity detection respects word boundaries."""
        filter = ProfanityFilter()
        # These should be clean (part of legitimate words)
        assert filter.contains_profanity("assessment") is False
        assert filter.contains_profanity("class assignment") is False
        # But these should be flagged
        assert filter.contains_profanity("what the hell") is True
    
    def test_filter_text(self):
        """Test text filtering with replacement."""
        filter = ProfanityFilter()
        filtered = filter.filter_text("This is fucking amazing")
        assert "fucking" not in filtered
        assert "***" in filtered
    
    def test_check_content_returns_tuple(self):
        """Test that check_content returns proper tuple."""
        filter = ProfanityFilter()
        is_clean, message = filter.check_content("Clean text")
        assert is_clean is True
        assert "appropriate" in message.lower()
        
        is_clean, message = filter.check_content("This is shit")
        assert is_clean is False
        assert "inappropriate" in message.lower()


class TestContentModerationHelpers:
    """Test content moderation helper functions."""
    
    def test_check_deck_content_clean(self):
        """Test deck content checking with clean text."""
        is_clean, message = check_deck_content("Contract Law", "Study deck for contracts")
        assert is_clean is True
    
    def test_check_deck_content_profanity_in_name(self):
        """Test deck content checking with profanity in name."""
        is_clean, message = check_deck_content("Fucking Law", "Study deck")
        assert is_clean is False
        assert "name" in message.lower()
    
    def test_check_deck_content_profanity_in_description(self):
        """Test deck content checking with profanity in description."""
        is_clean, message = check_deck_content("Contract Law", "This shit is hard")
        assert is_clean is False
        assert "description" in message.lower()
    
    def test_check_card_content_clean(self):
        """Test card content checking with clean text."""
        is_clean, message = check_card_content(
            "What is consideration?", 
            "A bargained-for exchange"
        )
        assert is_clean is True
    
    def test_check_card_content_profanity_in_front(self):
        """Test card content checking with profanity in front."""
        is_clean, message = check_card_content(
            "What the hell is consideration?",
            "A bargained-for exchange"
        )
        assert is_clean is False
        assert "front" in message.lower()
    
    def test_check_card_content_profanity_in_back(self):
        """Test card content checking with profanity in back."""
        is_clean, message = check_card_content(
            "What is consideration?",
            "I don't give a shit"
        )
        assert is_clean is False
        assert "back" in message.lower()


class TestDeckModerationIntegration:
    """Test deck creation/update with moderation."""
    
    def test_create_deck_with_clean_content(self, client: TestClient, auth_token: str):
        """Test creating a deck with clean content."""
        response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck for contracts",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Contract Law"
    
    def test_create_deck_with_profanity_in_name(self, client: TestClient, auth_token: str):
        """Test creating a deck with profanity in name is rejected."""
        response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Fucking Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_create_deck_with_profanity_in_description(self, client: TestClient, auth_token: str):
        """Test creating a deck with profanity in description is rejected."""
        response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "This shit is hard to learn",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_update_deck_with_profanity(self, client: TestClient, auth_token: str):
        """Test updating a deck with profanity is rejected."""
        # Create a clean deck first
        create_response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        deck_id = create_response.json()["id"]
        
        # Try to update with profanity
        response = client.put(
            f"/api/v1/decks/{deck_id}",
            json={
                "name": "Damn Contract Law"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()


class TestCardModerationIntegration:
    """Test card creation/update with moderation."""
    
    def test_create_card_with_clean_content(self, client: TestClient, auth_token: str):
        """Test creating a card with clean content."""
        # Create a deck first
        deck_response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        deck_id = deck_response.json()["id"]
        
        # Create a card
        response = client.post(
            "/api/v1/cards/",
            json={
                "deck_id": deck_id,
                "front": "What is consideration?",
                "back": "A bargained-for exchange"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["front"] == "What is consideration?"
    
    def test_create_card_with_profanity_in_front(self, client: TestClient, auth_token: str):
        """Test creating a card with profanity in front is rejected."""
        # Create a deck first
        deck_response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        deck_id = deck_response.json()["id"]
        
        # Try to create card with profanity
        response = client.post(
            "/api/v1/cards/",
            json={
                "deck_id": deck_id,
                "front": "What the fuck is consideration?",
                "back": "A bargained-for exchange"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_create_card_with_profanity_in_back(self, client: TestClient, auth_token: str):
        """Test creating a card with profanity in back is rejected."""
        # Create a deck first
        deck_response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        deck_id = deck_response.json()["id"]
        
        # Try to create card with profanity
        response = client.post(
            "/api/v1/cards/",
            json={
                "deck_id": deck_id,
                "front": "What is consideration?",
                "back": "Who gives a shit about this"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_update_card_with_profanity(self, client: TestClient, auth_token: str):
        """Test updating a card with profanity is rejected."""
        # Create a deck and card first
        deck_response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Contract Law",
                "description": "Study deck",
                "is_public": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        deck_id = deck_response.json()["id"]
        
        card_response = client.post(
            "/api/v1/cards/",
            json={
                "deck_id": deck_id,
                "front": "What is consideration?",
                "back": "A bargained-for exchange"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        card_id = card_response.json()["id"]
        
        # Try to update with profanity
        response = client.put(
            f"/api/v1/cards/{card_id}",
            json={
                "back": "This damn definition is hard"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
