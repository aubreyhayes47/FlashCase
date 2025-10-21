"""Tests for user reporting functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.models.report import ReportType, ReportReason, ReportStatus


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


class TestReportCreation:
    """Test creating reports."""
    
    def test_create_report_success(self, client: TestClient, auth_token: str):
        """Test successfully creating a report."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "inappropriate_content",
                "description": "This deck contains offensive material"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["report_type"] == "deck"
        assert data["content_id"] == 1
        assert data["reason"] == "inappropriate_content"
        assert data["status"] == "pending"
        assert "id" in data
    
    def test_create_report_without_description(self, client: TestClient, auth_token: str):
        """Test creating a report without optional description."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "card",
                "content_id": 5,
                "reason": "spam"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
    
    def test_create_report_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot create reports."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_report_invalid_type(self, client: TestClient, auth_token: str):
        """Test creating a report with invalid type."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "invalid_type",
                "content_id": 1,
                "reason": "spam"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422


class TestReportListing:
    """Test listing reports."""
    
    def test_list_user_reports(self, client: TestClient, auth_token: str):
        """Test listing user's own reports."""
        # Create a few reports
        for i in range(3):
            client.post(
                "/api/v1/reports/",
                json={
                    "report_type": "deck",
                    "content_id": i + 1,
                    "reason": "spam"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # List reports
        response = client.get(
            "/api/v1/reports/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_list_reports_filtered_by_status(self, client: TestClient, auth_token: str):
        """Test listing reports filtered by status."""
        # Create a report
        client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # List pending reports
        response = client.get(
            "/api/v1/reports/?status_filter=pending",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
    
    def test_list_reports_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot list reports."""
        response = client.get("/api/v1/reports/")
        assert response.status_code == 401


class TestReportRetrieval:
    """Test retrieving individual reports."""
    
    def test_get_own_report(self, client: TestClient, auth_token: str):
        """Test getting user's own report."""
        # Create a report
        create_response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "card",
                "content_id": 10,
                "reason": "harassment",
                "description": "Harassment in card content"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        report_id = create_response.json()["id"]
        
        # Get the report
        response = client.get(
            f"/api/v1/reports/{report_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
        assert data["content_id"] == 10
    
    def test_get_nonexistent_report(self, client: TestClient, auth_token: str):
        """Test getting a report that doesn't exist."""
        response = client.get(
            "/api/v1/reports/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_other_user_report(self, client: TestClient, auth_token: str):
        """Test that users cannot view other users' reports."""
        # Create a report with first user
        create_response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        report_id = create_response.json()["id"]
        
        # Create second user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "testuser2",
                "password": "testpassword123"
            }
        )
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser2",
                "password": "testpassword123"
            }
        )
        token2 = login_response.json()["access_token"]
        
        # Try to access first user's report
        response = client.get(
            f"/api/v1/reports/{report_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403


class TestReportReasons:
    """Test different report reasons."""
    
    def test_report_spam(self, client: TestClient, auth_token: str):
        """Test reporting spam content."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["reason"] == "spam"
    
    def test_report_harassment(self, client: TestClient, auth_token: str):
        """Test reporting harassment."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "user",
                "content_id": 2,
                "reason": "harassment"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["reason"] == "harassment"
    
    def test_report_copyright(self, client: TestClient, auth_token: str):
        """Test reporting copyright violation."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 3,
                "reason": "copyright_violation",
                "description": "Content copied from copyrighted textbook"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["reason"] == "copyright_violation"
