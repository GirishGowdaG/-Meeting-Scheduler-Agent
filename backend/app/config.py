"""
Application Configuration
Centralized configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Google Gemini
    gemini_api_key: str
    
    # Application
    secret_key: str
    database_url: str = "sqlite:///./smartmeet.db"
    encryption_key: str
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
