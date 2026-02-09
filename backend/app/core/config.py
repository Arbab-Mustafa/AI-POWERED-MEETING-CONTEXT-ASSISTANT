"""
Core configuration module for ContextMeet backend.
Handles all settings, database initialization, and application setup.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ContextMeet"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/contextmeet"
    )
    DATABASE_ASYNC_URL: str = os.getenv(
        "DATABASE_ASYNC_URL",
        "postgresql+asyncpg://user:password@localhost:5432/contextmeet"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
    
    # Gmail
    GMAIL_EMAIL: str = os.getenv("GMAIL_EMAIL", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Mistral AI
    MISTRAL_BASE_URL: str = os.getenv("MISTRAL_BASE_URL", "http://localhost:11434")
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Sentry
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


class DatabaseManager:
    """Manages database connection and session handling."""
    
    def __init__(self):
        self.engine = None
        self.AsyncSessionLocal = None
    
    async def initialize(self):
        """Initialize async database engine and session factory."""
        self.engine = create_async_engine(
            settings.DATABASE_ASYNC_URL,
            echo=settings.DEBUG,
            future=True
        )
        self.AsyncSessionLocal = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        logger.info("Database engine initialized successfully")
    
    async def dispose(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")
    
    async def get_session(self) -> AsyncSession:
        """Get async database session."""
        if self.AsyncSessionLocal is None:
            await self.initialize()
        async with self.AsyncSessionLocal() as session:
            yield session


db_manager = DatabaseManager()


def configure_logging():
    """Configure application logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress verbose logging from libraries
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


configure_logging()


__all__ = [
    "Settings",
    "settings",
    "DatabaseManager",
    "db_manager",
    "configure_logging"
]
