from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./flashcase.db"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "FlashCase API"
    
    # AI/Grok
    grok_api_key: str = ""
    grok_api_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-4-fast"
    
    # AI Cost Control - Safe defaults optimized for cost
    grok_default_temperature: float = 0.7
    grok_default_max_tokens: int = 1500  # Reduced from 2000 for cost control
    grok_chat_max_tokens: int = 2000
    grok_rewrite_max_tokens: int = 1000  # Rewriting needs less tokens
    grok_autocomplete_max_tokens: int = 500  # Autocomplete needs minimal tokens
    
    # CourtListener API
    courtlistener_api_base_url: str = "https://www.courtlistener.com/api/rest/v3"
    courtlistener_api_key: str = ""
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100
    
    # AI-specific Rate Limiting (per user)
    ai_rate_limit_per_minute: int = 5  # More restrictive for AI calls
    ai_rate_limit_per_hour: int = 50
    
    # Token Usage Monitoring
    token_usage_alert_threshold: int = 100000  # Alert after 100k tokens per hour
    token_usage_tracking_enabled: bool = True
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
