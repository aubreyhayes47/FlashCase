"""Tests for reporting system."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.models.user import User
from app.models.report import Report, ReportStatus


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


@pytest.fixture(name="regular_user_headers")
def regular_user_headers_fixture(client: TestClient):
    """Create a regular test user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "regularuser",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "regularuser",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_user_headers")
def admin_user_headers_fixture(client: TestClient, session: Session):
    """Create an admin test user and return auth headers."""
    # Register admin user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "adminpass123"
        }
    )
    
    # Manually set user as admin
    statement = select(User).where(User.username == "adminuser")
    admin_user = session.exec(statement).first()
    admin_user.is_admin = True
    session.add(admin_user)
    session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "adminuser",
            "password": "adminpass123"
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestReportCreation:
    """Test report creation endpoint."""
    
    def test_create_report_success(self, client: TestClient, regular_user_headers: dict):
        """Test successful report creation."""
        response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "inappropriate",
                "description": "This deck contains offensive content"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["report_type"] == "deck"
        assert data["content_id"] == 1
        assert data["reason"] == "inappropriate"
        assert data["status"] == "pending"
        assert data["description"] == "This deck contains offensive content"
    
    def test_create_report_minimal(self, client: TestClient, regular_user_headers: dict):
        """Test report creation with minimal data."""
        response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "card",
                "content_id": 5,
                "reason": "spam"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["report_type"] == "card"
        assert data["content_id"] == 5
        assert data["reason"] == "spam"
        assert data["description"] is None
    
    def test_create_report_requires_auth(self, client: TestClient):
        """Test that report creation requires authentication."""
        response = client.post(
            "/api/v1/reports/",
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "inappropriate"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_report_invalid_type(self, client: TestClient, regular_user_headers: dict):
        """Test report creation with invalid type."""
        response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "invalid_type",
                "content_id": 1,
                "reason": "inappropriate"
            }
        )
        
        assert response.status_code == 422


class TestGetMyReports:
    """Test getting user's own reports."""
    
    def test_get_my_reports(self, client: TestClient, regular_user_headers: dict):
        """Test getting current user's reports."""
        # Create a report
        client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "inappropriate",
                "description": "Test report"
            }
        )
        
        # Get my reports
        response = client.get(
            "/api/v1/reports/my-reports",
            headers=regular_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "Test report"
    
    def test_get_my_reports_empty(self, client: TestClient, regular_user_headers: dict):
        """Test getting reports when user has none."""
        response = client.get(
            "/api/v1/reports/my-reports",
            headers=regular_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_my_reports_requires_auth(self, client: TestClient):
        """Test that getting reports requires authentication."""
        response = client.get("/api/v1/reports/my-reports")
        
        assert response.status_code == 401


class TestAdminReportOperations:
    """Test admin-only report operations."""
    
    def test_list_all_reports_as_admin(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict):
        """Test that admin can list all reports."""
        # Regular user creates a report
        client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "inappropriate"
            }
        )
        
        # Admin lists reports
        response = client.get(
            "/api/v1/reports/",
            headers=admin_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_list_reports_non_admin_forbidden(self, client: TestClient, regular_user_headers: dict):
        """Test that non-admin cannot list all reports."""
        response = client.get(
            "/api/v1/reports/",
            headers=regular_user_headers
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_get_specific_report_as_admin(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict):
        """Test that admin can get specific report."""
        # Create a report
        create_response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "card",
                "content_id": 2,
                "reason": "spam"
            }
        )
        report_id = create_response.json()["id"]
        
        # Admin gets report
        response = client.get(
            f"/api/v1/reports/{report_id}",
            headers=admin_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
    
    def test_get_report_non_admin_forbidden(self, client: TestClient, regular_user_headers: dict):
        """Test that non-admin cannot get specific report."""
        response = client.get(
            "/api/v1/reports/1",
            headers=regular_user_headers
        )
        
        assert response.status_code == 403
    
    def test_update_report_as_admin(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict):
        """Test that admin can update report status."""
        # Create a report
        create_response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 3,
                "reason": "copyright"
            }
        )
        report_id = create_response.json()["id"]
        
        # Admin updates report
        response = client.put(
            f"/api/v1/reports/{report_id}",
            headers=admin_user_headers,
            json={
                "status": "reviewed",
                "admin_notes": "Reviewed and confirmed violation"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reviewed"
        assert data["admin_notes"] == "Reviewed and confirmed violation"
        assert data["reviewed_by"] is not None
    
    def test_update_report_non_admin_forbidden(self, client: TestClient, regular_user_headers: dict):
        """Test that non-admin cannot update report."""
        response = client.put(
            "/api/v1/reports/1",
            headers=regular_user_headers,
            json={
                "status": "reviewed",
                "admin_notes": "Test"
            }
        )
        
        assert response.status_code == 403
    
    def test_delete_report_as_admin(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict):
        """Test that admin can delete report."""
        # Create a report
        create_response = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 4,
                "reason": "other"
            }
        )
        report_id = create_response.json()["id"]
        
        # Admin deletes report
        response = client.delete(
            f"/api/v1/reports/{report_id}",
            headers=admin_user_headers
        )
        
        assert response.status_code == 204
        
        # Verify report is deleted
        get_response = client.get(
            f"/api/v1/reports/{report_id}",
            headers=admin_user_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_report_non_admin_forbidden(self, client: TestClient, regular_user_headers: dict):
        """Test that non-admin cannot delete report."""
        response = client.delete(
            "/api/v1/reports/1",
            headers=regular_user_headers
        )
        
        assert response.status_code == 403


class TestReportFiltering:
    """Test report filtering functionality."""
    
    def test_filter_reports_by_status(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict, session: Session):
        """Test filtering reports by status."""
        # Create reports with different statuses
        report1 = client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            }
        )
        report1_id = report1.json()["id"]
        
        client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "card",
                "content_id": 2,
                "reason": "spam"
            }
        )
        
        # Update one report status
        client.put(
            f"/api/v1/reports/{report1_id}",
            headers=admin_user_headers,
            json={
                "status": "reviewed"
            }
        )
        
        # Filter by pending
        response = client.get(
            "/api/v1/reports/?status_filter=pending",
            headers=admin_user_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        # Filter by reviewed
        response = client.get(
            "/api/v1/reports/?status_filter=reviewed",
            headers=admin_user_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_filter_reports_by_type(self, client: TestClient, regular_user_headers: dict, admin_user_headers: dict):
        """Test filtering reports by type."""
        # Create reports of different types
        client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "deck",
                "content_id": 1,
                "reason": "spam"
            }
        )
        
        client.post(
            "/api/v1/reports/",
            headers=regular_user_headers,
            json={
                "report_type": "card",
                "content_id": 2,
                "reason": "spam"
            }
        )
        
        # Filter by deck
        response = client.get(
            "/api/v1/reports/?report_type=deck",
            headers=admin_user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(r["report_type"] == "deck" for r in data)
        
        # Filter by card
        response = client.get(
            "/api/v1/reports/?report_type=card",
            headers=admin_user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(r["report_type"] == "card" for r in data)
