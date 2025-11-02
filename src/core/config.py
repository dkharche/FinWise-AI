"""Configuration management for FinWise-AI."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    ENVIRONMENT: str = Field(default="development")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    
    # Vector Database
    VECTOR_DB_TYPE: str = Field(default="chroma")
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma")
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # MLflow
    MLFLOW_TRACKING_URI: Optional[str] = Field(default=None)
    
    # Security
    SECRET_KEY: str = Field(default="change-this-secret-key")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    
    # Model Configuration
    DEFAULT_LLM_MODEL: str = Field(default="gpt-4")
    DEFAULT_EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002")
    MAX_TOKENS: int = Field(default=4096)
    TEMPERATURE: float = Field(default=0.7)
    
    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=50)
    ALLOWED_FILE_TYPES: List[str] = Field(default=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Global settings instance
settings = Settings()