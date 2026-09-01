"""
SQLAlchemy MySQL Connection Manager using PyMySQL driver.
Provides pooled database connections, sessions, and health verification.
"""

import time
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()


def get_engine() -> Engine:
    """
    Create and configure SQLAlchemy Engine with robust connection pooling.
    Uses pure-Python PyMySQL driver.
    """
    return create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
    )


engine: Engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and closes it on exit.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection() -> Tuple[bool, str, float]:
    """
    Test connectivity to the MySQL database.
    Returns (success: bool, message: str, latency_ms: float).
    """
    start_time = time.time()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS alive, DATABASE() AS current_db;"))
            row = result.fetchone()
            latency_ms = (time.time() - start_time) * 1000
            db_name = row[1] if row else "unknown"
            logger.info(f"Database connection verified: connected to `{db_name}` in {latency_ms:.2f}ms")
            return True, f"Connected to {db_name}", latency_ms
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        err_msg = f"Database connection failed: {str(e)}"
        logger.error(err_msg)
        return False, err_msg, latency_ms
