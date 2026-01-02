"""
Configuration settings for the Campus Assistant Chatbot.
Uses pydantic-settings for environment variable management.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App info
    app_name: str = "Campus Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-this-in-production"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/chatbot.db"

    # LLM Configuration
    llm_provider: str = "gemini"  # "gemini" or "openai"
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Bhashini Translation API
    bhashini_user_id: Optional[str] = None
    bhashini_api_key: Optional[str] = None
    bhashini_pipeline_id: Optional[str] = None

    # Google Translate fallback
    google_translate_api_key: Optional[str] = None

    # Telegram
    telegram_bot_token: Optional[str] = None

    # Twilio/WhatsApp
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "./data/logs/chatbot.log"

    # Vector DB settings
    chroma_persist_directory: str = "./data/chroma"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Supported languages
    supported_languages: List[str] = Field(
        default=["en", "hi", "raj", "gu", "mr", "pa", "ta"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Language code mappings
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "raj": "Rajasthani",
    "gu": "Gujarati",
    "mr": "Marathi",
    "pa": "Punjabi",
    "ta": "Tamil",
    "bn": "Bengali",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
}

# Bhashini language codes mapping
BHASHINI_LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "gu": "gu",
    "mr": "mr",
    "pa": "pa",
    "ta": "ta",
    "bn": "bn",
    "te": "te",
    "kn": "kn",
    "ml": "ml",
    "or": "or",
    "raj": "hi",  # Rajasthani falls back to Hindi
}
