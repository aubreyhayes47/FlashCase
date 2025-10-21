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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
