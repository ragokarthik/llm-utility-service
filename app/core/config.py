from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Document Extraction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./extraction.db"

    # LLM
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.1-70b-versatile"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
