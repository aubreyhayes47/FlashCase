"""Tests for protected endpoints requiring authentication."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.core.database import get_session


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
    """Create a user and return authentication token."""
    # Register user
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


class TestProtectedDeckEndpoints:
    """Test deck endpoints require authentication."""
    
    def test_list_decks_requires_auth(self, client: TestClient):
        """Test that listing decks requires authentication."""
        response = client.get("/api/v1/decks/")
        assert response.status_code == 401
    
    def test_list_decks_with_auth(self, client: TestClient, auth_token: str):
        """Test that listing decks works with authentication."""
        response = client.get(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_deck_requires_auth(self, client: TestClient):
        """Test that getting a deck requires authentication."""
        response = client.get("/api/v1/decks/1")
        assert response.status_code == 401
    
    def test_create_deck_requires_auth(self, client: TestClient):
        """Test that creating a deck requires authentication."""
        response = client.post(
            "/api/v1/decks/",
            json={
                "name": "Test Deck",
                "description": "Test Description"
            }
        )
        assert response.status_code == 401
    
    def test_create_deck_with_auth(self, client: TestClient, auth_token: str):
        """Test creating a deck with authentication."""
        response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Deck",
                "description": "Test Description",
                "is_public": False
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Deck"
        assert data["description"] == "Test Description"
        assert data["is_public"] is False
        assert "id" in data
    
    def test_update_deck_requires_auth(self, client: TestClient, auth_token: str):
        """Test that updating a deck requires authentication."""
        # Create a deck first
        create_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Original Name",
                "description": "Original Description"
            }
        )
        deck_id = create_response.json()["id"]
        
        # Try to update without auth
        response = client.put(
            f"/api/v1/decks/{deck_id}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 401
    
    def test_update_deck_with_auth(self, client: TestClient, auth_token: str):
        """Test updating a deck with authentication."""
        # Create a deck
        create_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Original Name",
                "description": "Original Description"
            }
        )
        deck_id = create_response.json()["id"]
        
        # Update the deck
        response = client.put(
            f"/api/v1/decks/{deck_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Original Description"  # Should be unchanged
    
    def test_delete_deck_requires_auth(self, client: TestClient, auth_token: str):
        """Test that deleting a deck requires authentication."""
        # Create a deck first
        create_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Deck"
            }
        )
        deck_id = create_response.json()["id"]
        
        # Try to delete without auth
        response = client.delete(f"/api/v1/decks/{deck_id}")
        assert response.status_code == 401


class TestProtectedCardEndpoints:
    """Test card endpoints require authentication."""
    
    def test_list_cards_requires_auth(self, client: TestClient):
        """Test that listing cards requires authentication."""
        response = client.get("/api/v1/cards/")
        assert response.status_code == 401
    
    def test_list_cards_with_auth(self, client: TestClient, auth_token: str):
        """Test that listing cards works with authentication."""
        response = client.get(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_card_requires_auth(self, client: TestClient):
        """Test that creating a card requires authentication."""
        response = client.post(
            "/api/v1/cards/",
            json={
                "deck_id": 1,
                "front": "Question",
                "back": "Answer"
            }
        )
        assert response.status_code == 401
    
    def test_create_card_with_auth(self, client: TestClient, auth_token: str):
        """Test creating a card with authentication."""
        # Create a deck first
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        # Create a card
        response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "deck_id": deck_id,
                "front": "What is FastAPI?",
                "back": "A modern Python web framework"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["front"] == "What is FastAPI?"
        assert data["back"] == "A modern Python web framework"
        assert data["deck_id"] == deck_id
    
    def test_update_card_requires_auth(self, client: TestClient, auth_token: str):
        """Test that updating a card requires authentication."""
        # Create deck and card first
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        card_response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "deck_id": deck_id,
                "front": "Question",
                "back": "Answer"
            }
        )
        card_id = card_response.json()["id"]
        
        # Try to update without auth
        response = client.put(
            f"/api/v1/cards/{card_id}",
            json={"front": "Updated Question"}
        )
        assert response.status_code == 401
    
    def test_update_card_with_auth(self, client: TestClient, auth_token: str):
        """Test updating a card with authentication."""
        # Create deck and card
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        card_response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "deck_id": deck_id,
                "front": "Original Question",
                "back": "Original Answer"
            }
        )
        card_id = card_response.json()["id"]
        
        # Update the card
        response = client.put(
            f"/api/v1/cards/{card_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"front": "Updated Question"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["front"] == "Updated Question"
        assert data["back"] == "Original Answer"  # Should be unchanged


class TestProtectedStudyEndpoints:
    """Test study endpoints require authentication."""
    
    def test_get_study_session_requires_auth(self, client: TestClient):
        """Test that getting study session requires authentication."""
        response = client.get("/api/v1/study/session/1")
        assert response.status_code == 401
    
    def test_get_study_session_with_auth(self, client: TestClient, auth_token: str):
        """Test getting study session with authentication."""
        # Create a deck first
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        # Get study session
        response = client.get(
            f"/api/v1/study/session/{deck_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_review_card_requires_auth(self, client: TestClient):
        """Test that reviewing a card requires authentication."""
        response = client.post(
            "/api/v1/study/review/1",
            json={"quality": 5}
        )
        assert response.status_code == 401
    
    def test_review_card_with_auth(self, client: TestClient, auth_token: str):
        """Test reviewing a card with authentication."""
        # Create deck and card
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        card_response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "deck_id": deck_id,
                "front": "Question",
                "back": "Answer"
            }
        )
        card_id = card_response.json()["id"]
        
        # Review the card
        response = client.post(
            f"/api/v1/study/review/{card_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"quality": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["card_id"] == card_id
        assert data["quality"] == 5
        assert "new_ease_factor" in data
        assert "new_interval" in data
        assert "next_due_date" in data


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_deck_creation_validation(self, client: TestClient, auth_token: str):
        """Test deck creation validates required fields."""
        # Missing required field 'name'
        response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"description": "Test"}
        )
        assert response.status_code == 422
    
    def test_card_creation_validation(self, client: TestClient, auth_token: str):
        """Test card creation validates required fields."""
        # Missing required fields
        response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"deck_id": 1}
        )
        assert response.status_code == 422
    
    def test_card_front_too_long(self, client: TestClient, auth_token: str):
        """Test card front text length validation."""
        # Create deck first
        deck_response = client.post(
            "/api/v1/decks/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Deck"}
        )
        deck_id = deck_response.json()["id"]
        
        # Try to create card with front text too long (>2000 chars)
        response = client.post(
            "/api/v1/cards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "deck_id": deck_id,
                "front": "x" * 2001,
                "back": "Answer"
            }
        )
        assert response.status_code == 422
