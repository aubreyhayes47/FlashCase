"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.models.user import User


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


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_user_success(self, client: TestClient, session: Session):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_user_duplicate_username(self, client: TestClient, session: Session):
        """Test registration with duplicate username."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "testuser",
                "password": "password456"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_user_duplicate_email(self, client: TestClient, session: Session):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "user1",
                "password": "password123"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "user2",
                "password": "password456"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_user_short_password(self, client: TestClient):
        """Test registration with password too short."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_user_short_username(self, client: TestClient):
        """Test registration with username too short."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "ab",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client: TestClient):
        """Test successful login."""
        # Register a user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        # Login with correct credentials
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password."""
        # Register a user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "correctpassword"
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent username."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


class TestGetCurrentUser:
    """Test get current user endpoint."""
    
    def test_get_current_user_success(self, client: TestClient):
        """Test getting current user with valid token."""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert "hashed_password" not in data
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_password_is_hashed(self, client: TestClient, session: Session):
        """Test that passwords are hashed in database."""
        password = "testpassword123"
        
        # Register a user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": password
            }
        )
        
        # Check that password is hashed in database
        from sqlmodel import select
        statement = select(User).where(User.username == "testuser")
        user = session.exec(statement).first()
        
        assert user is not None
        assert user.hashed_password != password
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash prefix


class TestJWTTokenValidation:
    """Test JWT token validation."""
    
    def test_token_contains_user_info(self, client: TestClient):
        """Test that JWT token contains correct user information."""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Decode token and verify
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert "user_id" in payload
        assert "exp" in payload
    
    def test_expired_token_rejected(self, client: TestClient):
        """Test that expired tokens are rejected."""
        from datetime import timedelta
        from app.core.security import create_access_token
        
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": "testuser", "user_id": 1},
            expires_delta=timedelta(seconds=-1)
        )
        
        # Try to use expired token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
