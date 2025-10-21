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
    grok_model: str = "grok-beta"
    
    # CourtListener API
    courtlistener_api_base_url: str = "https://www.courtlistener.com/api/rest/v3"
    courtlistener_api_key: str = ""
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
