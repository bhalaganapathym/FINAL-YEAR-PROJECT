"""
Application configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""

import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and environment configuration.
    """
    # AI Configuration
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"

    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "business_analytics"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    # Backend Server Configuration
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Memory & Checkpointing
    MEMORY_DB_PATH: str = "./memory/checkpoints.db"

    # Safety & Execution Rules
    MAX_RETRY_COUNT: int = 3
    QUERY_TIMEOUT: int = 30
    MAX_RESULT_ROWS: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=os.path.join(Path(__file__).resolve().parent.parent, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """
        Generate SQLAlchemy MySQL connection URL using pure-Python PyMySQL driver.
        Format: mysql+pymysql://user:password@host:port/dbname
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached Settings instance.
    """
    return Settings()
