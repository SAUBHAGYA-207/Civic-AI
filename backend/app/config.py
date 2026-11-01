import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "CivicPulse AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Model configuration
    OLLAMA_HOST: str = "http://localhost:11434"
    VISION_MODEL: str = "qwen2.5vl:3b"
    TEXT_MODEL: str = "qwen2.5:1.5b"
    MODEL_TIMEOUT_SECONDS: int = 120
    MODEL_MAX_RETRIES: int = 2
    
    # Storage & Upload limits
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB per image
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_MIME_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp"}
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'civicpulse.db'}"
    
    # Reviewer Authorization Token (for reviewer updates)
    REVIEWER_SECRET_KEY: str = "civicpulse-reviewer-dev-key-secure"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://frontend-woad-ten-72.vercel.app",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
