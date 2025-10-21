"""
Tests for AI cost control features including token tracking and rate limiting.

These tests verify the new cost control mechanisms for the grok-4-fast model.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.grok_service import GrokService

client = TestClient(app)


class TestAICostControlConfig:
    """Tests for AI cost control configuration."""
    
    def test_grok_4_fast_configured(self):
        """Test that grok-4-fast is the default model."""
        assert settings.grok_model == "grok-4-fast"
    
    def test_cost_controlled_defaults_exist(self):
        """Test that cost-controlled default parameters are configured."""
        assert hasattr(settings, "grok_default_temperature")
        assert hasattr(settings, "grok_default_max_tokens")
        assert hasattr(settings, "grok_chat_max_tokens")
        assert hasattr(settings, "grok_rewrite_max_tokens")
        assert hasattr(settings, "grok_autocomplete_max_tokens")
        
        # Verify reasonable defaults for cost control
        assert settings.grok_default_temperature == 0.7
        assert settings.grok_chat_max_tokens <= 2000
        assert settings.grok_rewrite_max_tokens <= settings.grok_chat_max_tokens
        assert settings.grok_autocomplete_max_tokens <= settings.grok_rewrite_max_tokens
    
    def test_ai_specific_rate_limits_configured(self):
        """Test that AI-specific rate limits are more restrictive."""
        assert hasattr(settings, "ai_rate_limit_per_minute")
        assert hasattr(settings, "ai_rate_limit_per_hour")
        
        # AI rate limits should be more restrictive than general limits
        assert settings.ai_rate_limit_per_minute <= settings.rate_limit_per_minute
        assert settings.ai_rate_limit_per_hour <= settings.rate_limit_per_hour
    
    def test_token_usage_tracking_configured(self):
        """Test that token usage tracking is configured."""
        assert hasattr(settings, "token_usage_tracking_enabled")
        assert hasattr(settings, "token_usage_alert_threshold")
        assert settings.token_usage_tracking_enabled == True
        assert settings.token_usage_alert_threshold > 0


class TestTokenUsageTracking:
    """Tests for token usage tracking functionality."""
    
    def test_token_usage_stats_initialized(self):
        """Test that token usage statistics are properly initialized."""
        # Reset stats for clean test
        GrokService.reset_token_usage_stats()
        
        stats = GrokService.get_token_usage_stats()
        assert "total_prompt_tokens" in stats
        assert "total_completion_tokens" in stats
        assert "total_tokens" in stats
        assert "total_requests" in stats
        assert stats["total_tokens"] == 0
        assert stats["total_requests"] == 0
    
    def test_token_usage_reset(self):
        """Test that token usage statistics can be reset."""
        # Manually set some values
        GrokService._token_usage["total_tokens"] = 1000
        GrokService._token_usage["total_requests"] = 10
        
        # Reset
        GrokService.reset_token_usage_stats()
        
        # Verify reset
        stats = GrokService.get_token_usage_stats()
        assert stats["total_tokens"] == 0
        assert stats["total_requests"] == 0


class TestTokenUsageEndpoint:
    """Tests for the token usage monitoring endpoint."""
    
    def test_usage_endpoint_exists(self):
        """Test that the usage endpoint is accessible."""
        response = client.get("/api/v1/ai/usage")
        assert response.status_code == 200
    
    def test_usage_endpoint_returns_stats(self):
        """Test that usage endpoint returns proper statistics."""
        # Reset stats for clean test
        GrokService.reset_token_usage_stats()
        
        response = client.get("/api/v1/ai/usage")
        assert response.status_code == 200
        
        data = response.json()
        assert "usage" in data
        assert "alert_threshold" in data
        assert "alert_triggered" in data
        assert "cost_control" in data
        
        # Check usage structure
        assert "total_prompt_tokens" in data["usage"]
        assert "total_completion_tokens" in data["usage"]
        assert "total_tokens" in data["usage"]
        assert "total_requests" in data["usage"]
        
        # Check cost_control structure
        assert "model" in data["cost_control"]
        assert "default_temperature" in data["cost_control"]
        assert "max_tokens" in data["cost_control"]
        assert data["cost_control"]["model"] == "grok-4-fast"
    
    def test_usage_endpoint_alert_threshold(self):
        """Test that alert is properly triggered when threshold is exceeded."""
        # Reset stats
        GrokService.reset_token_usage_stats()
        
        # Simulate high usage
        GrokService._token_usage["total_tokens"] = settings.token_usage_alert_threshold + 1000
        
        response = client.get("/api/v1/ai/usage")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alert_triggered"] == True
        
        # Reset for other tests
        GrokService.reset_token_usage_stats()


class TestAIHealthEndpointEnhanced:
    """Tests for enhanced AI health endpoint with cost control info."""
    
    def test_health_endpoint_includes_rate_limits(self):
        """Test that health endpoint includes AI rate limit information."""
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "ai_rate_limits" in data
        assert "per_minute" in data["ai_rate_limits"]
        assert "per_hour" in data["ai_rate_limits"]
        assert data["model"] == "grok-4-fast"


class TestCostControlledDefaults:
    """Tests that endpoints use cost-controlled defaults."""
    
    def test_grok_service_uses_controlled_defaults(self):
        """Test that GrokService uses cost-controlled defaults when not specified."""
        service = GrokService()
        
        # The service should use settings for defaults
        assert service.model == settings.grok_model
        assert service.model == "grok-4-fast"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
