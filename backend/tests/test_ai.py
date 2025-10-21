"""
Tests for AI endpoints and Grok service.

These tests verify the AI functionality including chat, card rewriting,
and autocomplete features, as well as rate limiting.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.core.config import settings

client = TestClient(app)


class TestAIHealthEndpoint:
    """Tests for AI health check endpoint."""
    
    def test_ai_health_check(self):
        """Test AI health check endpoint returns correct status."""
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "grok_configured" in data
        assert "courtlistener_configured" in data
        assert "model" in data
        assert "rate_limiting_enabled" in data


class TestAIChatEndpoint:
    """Tests for AI chat endpoint."""
    
    def test_chat_requires_grok_api_key(self):
        """Test chat endpoint returns error when Grok API key is not configured."""
        # Save original key
        original_key = settings.grok_api_key
        settings.grok_api_key = ""
        
        try:
            response = client.post(
                "/api/v1/ai/chat",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "stream": False
                }
            )
            assert response.status_code == 503
            assert "not configured" in response.json()["detail"]
        finally:
            # Restore original key
            settings.grok_api_key = original_key
    
    @patch('app.services.grok_service.GrokService.chat_completion')
    def test_chat_with_valid_request(self, mock_chat):
        """Test chat endpoint with valid request."""
        # Mock the chat completion to return a simple response
        async def mock_generator():
            yield "Test response"
        
        mock_chat.return_value = mock_generator()
        
        # Set API key for test
        original_key = settings.grok_api_key
        settings.grok_api_key = "test_key"
        
        try:
            response = client.post(
                "/api/v1/ai/chat",
                json={
                    "messages": [{"role": "user", "content": "What is jurisdiction?"}],
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            assert response.status_code == 200
        finally:
            settings.grok_api_key = original_key


class TestRewriteCardEndpoint:
    """Tests for card rewrite endpoint."""
    
    def test_rewrite_card_requires_grok_api_key(self):
        """Test rewrite-card endpoint returns error when Grok API key is not configured."""
        original_key = settings.grok_api_key
        settings.grok_api_key = ""
        
        try:
            response = client.post(
                "/api/v1/ai/rewrite-card",
                json={
                    "front": "What is jurisdiction?",
                    "back": "The power of a court to hear a case."
                }
            )
            assert response.status_code == 503
            assert "not configured" in response.json()["detail"]
        finally:
            settings.grok_api_key = original_key


class TestAutocompleteCardEndpoint:
    """Tests for card autocomplete endpoint."""
    
    def test_autocomplete_card_requires_grok_api_key(self):
        """Test autocomplete-card endpoint returns error when Grok API key is not configured."""
        original_key = settings.grok_api_key
        settings.grok_api_key = ""
        
        try:
            response = client.post(
                "/api/v1/ai/autocomplete-card",
                json={
                    "partial_text": "What is the Fourth",
                    "card_type": "front"
                }
            )
            assert response.status_code == 503
            assert "not configured" in response.json()["detail"]
        finally:
            settings.grok_api_key = original_key
    
    def test_autocomplete_card_invalid_type(self):
        """Test autocomplete-card endpoint rejects invalid card_type."""
        original_key = settings.grok_api_key
        settings.grok_api_key = "test_key"
        
        try:
            response = client.post(
                "/api/v1/ai/autocomplete-card",
                json={
                    "partial_text": "What is",
                    "card_type": "invalid"
                }
            )
            assert response.status_code == 400
            assert "must be either 'front' or 'back'" in response.json()["detail"]
        finally:
            settings.grok_api_key = original_key


class TestCourtListenerSearch:
    """Tests for CourtListener search tool."""
    
    @pytest.mark.asyncio
    @patch('app.services.grok_service.httpx.AsyncClient')
    async def test_search_courtlistener_success(self, mock_client):
        """Test successful CourtListener search."""
        from app.services.grok_service import search_courtlistener
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 2,
            "results": [
                {
                    "caseName": "Miranda v. Arizona",
                    "citation": ["384 U.S. 436"],
                    "court": "scotus",
                    "dateFiled": "1966-06-13",
                    "snippet": "The person must be warned...",
                    "absolute_url": "/opinion/107252/miranda-v-arizona/"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        # Mock the client context manager
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Call the function
        result = await search_courtlistener("Miranda rights")
        
        assert result["count"] == 2
        assert len(result["results"]) == 1
        assert result["results"][0]["case_name"] == "Miranda v. Arizona"
    
    @pytest.mark.asyncio
    @patch('app.services.grok_service.httpx.AsyncClient')
    async def test_search_courtlistener_error(self, mock_client):
        """Test CourtListener search handles errors gracefully."""
        from app.services.grok_service import search_courtlistener
        
        # Mock an HTTP error
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(side_effect=Exception("API Error"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Call the function
        result = await search_courtlistener("test query")
        
        assert "error" in result
        assert result["count"] == 0
        assert result["results"] == []


class TestRateLimiting:
    """Tests for rate limiting functionality."""
    
    def test_rate_limiting_configured(self):
        """Test that rate limiting is properly configured."""
        from app.middleware.rate_limit import limiter
        
        assert limiter is not None
        assert settings.rate_limit_enabled == True
        assert settings.rate_limit_per_minute > 0
        assert settings.rate_limit_per_hour > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
