"""Tests for content moderation functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.services.content_moderation import (
    is_content_appropriate,
    censor_text,
    validate_deck_content,
    validate_card_content
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


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    """Create a test user and return auth headers."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestContentModerationService:
    """Test content moderation service functions."""
    
    def test_appropriate_content(self):
        """Test that clean content passes validation."""
        is_appropriate, reason = is_content_appropriate("This is a legal case study")
        assert is_appropriate is True
        assert reason == ""
    
    def test_inappropriate_content(self):
        """Test that profane content is detected."""
        is_appropriate, reason = is_content_appropriate("This damn thing")
        assert is_appropriate is False
        assert "inappropriate" in reason.lower()
    
    def test_empty_content(self):
        """Test that empty content is allowed."""
        is_appropriate, reason = is_content_appropriate("")
        assert is_appropriate is True
        assert reason == ""
    
    def test_censor_text(self):
        """Test text censoring functionality."""
        censored = censor_text("This is a damn test")
        assert "damn" not in censored.lower()
        assert "*" in censored
    
    def test_validate_deck_content_clean(self):
        """Test deck validation with clean content."""
        is_valid, error = validate_deck_content("Criminal Law 101", "Study materials for criminal law")
        assert is_valid is True
        assert error == ""
    
    def test_validate_deck_content_dirty_name(self):
        """Test deck validation with inappropriate name."""
        is_valid, error = validate_deck_content("Damn Law", "Clean description")
        assert is_valid is False
        assert "name" in error.lower()
    
    def test_validate_deck_content_dirty_description(self):
        """Test deck validation with inappropriate description."""
        is_valid, error = validate_deck_content("Clean Name", "This damn description")
        assert is_valid is False
        assert "description" in error.lower()
    
    def test_validate_card_content_clean(self):
        """Test card validation with clean content."""
        is_valid, error = validate_card_content("What is tort law?", "A civil wrong")
        assert is_valid is True
        assert error == ""
    
    def test_validate_card_content_dirty_front(self):
        """Test card validation with inappropriate front."""
        is_valid, error = validate_card_content("What the hell is this?", "Clean answer")
        assert is_valid is False
        assert "front" in error.lower()
    
    def test_validate_card_content_dirty_back(self):
        """Test card validation with inappropriate back."""
        is_valid, error = validate_card_content("Clean question?", "This damn answer")
        assert is_valid is False
        assert "back" in error.lower()


class TestDeckContentModeration:
    """Test content moderation on deck endpoints."""
    
    def test_create_deck_with_clean_content(self, client: TestClient, auth_headers: dict):
        """Test creating a deck with appropriate content."""
        response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Constitutional Law",
                "description": "Study materials for constitutional law",
                "is_public": True
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Constitutional Law"
    
    def test_create_deck_with_profanity_in_name(self, client: TestClient, auth_headers: dict):
        """Test that deck creation is blocked with profanity in name."""
        response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Damn Law Cases",
                "description": "Clean description",
                "is_public": True
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_create_deck_with_profanity_in_description(self, client: TestClient, auth_headers: dict):
        """Test that deck creation is blocked with profanity in description."""
        response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Criminal Law",
                "description": "This damn course is hard",
                "is_public": True
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_update_deck_with_profanity(self, client: TestClient, auth_headers: dict):
        """Test that deck update is blocked with profanity."""
        # First create a clean deck
        create_response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Criminal Law",
                "description": "Clean description",
                "is_public": True
            }
        )
        deck_id = create_response.json()["id"]
        
        # Try to update with profanity
        response = client.put(
            f"/api/v1/decks/{deck_id}",
            headers=auth_headers,
            json={
                "name": "Damn Criminal Law"
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()


class TestCardContentModeration:
    """Test content moderation on card endpoints."""
    
    def test_create_card_with_clean_content(self, client: TestClient, auth_headers: dict):
        """Test creating a card with appropriate content."""
        # First create a deck
        deck_response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Torts",
                "description": "Tort law deck",
                "is_public": True
            }
        )
        deck_id = deck_response.json()["id"]
        
        # Create card
        response = client.post(
            "/api/v1/cards/",
            headers=auth_headers,
            json={
                "deck_id": deck_id,
                "front": "What is negligence?",
                "back": "Failure to exercise reasonable care"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["front"] == "What is negligence?"
    
    def test_create_card_with_profanity_in_front(self, client: TestClient, auth_headers: dict):
        """Test that card creation is blocked with profanity in front."""
        # First create a deck
        deck_response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Torts",
                "description": "Tort law deck",
                "is_public": True
            }
        )
        deck_id = deck_response.json()["id"]
        
        # Try to create card with profanity
        response = client.post(
            "/api/v1/cards/",
            headers=auth_headers,
            json={
                "deck_id": deck_id,
                "front": "What the hell is negligence?",
                "back": "Clean answer"
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_create_card_with_profanity_in_back(self, client: TestClient, auth_headers: dict):
        """Test that card creation is blocked with profanity in back."""
        # First create a deck
        deck_response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Torts",
                "description": "Tort law deck",
                "is_public": True
            }
        )
        deck_id = deck_response.json()["id"]
        
        # Try to create card with profanity
        response = client.post(
            "/api/v1/cards/",
            headers=auth_headers,
            json={
                "deck_id": deck_id,
                "front": "What is negligence?",
                "back": "It's when someone acts like a damn fool"
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
    
    def test_update_card_with_profanity(self, client: TestClient, auth_headers: dict):
        """Test that card update is blocked with profanity."""
        # Create deck and card
        deck_response = client.post(
            "/api/v1/decks/",
            headers=auth_headers,
            json={
                "name": "Torts",
                "description": "Tort law deck",
                "is_public": True
            }
        )
        deck_id = deck_response.json()["id"]
        
        card_response = client.post(
            "/api/v1/cards/",
            headers=auth_headers,
            json={
                "deck_id": deck_id,
                "front": "What is negligence?",
                "back": "Failure to exercise reasonable care"
            }
        )
        card_id = card_response.json()["id"]
        
        # Try to update with profanity
        response = client.put(
            f"/api/v1/cards/{card_id}",
            headers=auth_headers,
            json={
                "back": "It's when you act like a damn fool"
            }
        )
        
        assert response.status_code == 400
        assert "inappropriate" in response.json()["detail"].lower()
