"""
Persistent Checkpointing Manager for LangGraph Multi-Agent Memory.
Uses SQLite SqliteSaver for durable, stateful multi-turn conversational memory.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()


def get_memory_db_path() -> Path:
    """
    Ensure parent directories exist and return absolute Path to SQLite database.
    """
    configured_path = settings.MEMORY_DB_PATH
    if os.path.isabs(configured_path):
        db_path = Path(configured_path)
    else:
        # Relative to project root
        base_dir = Path(__file__).resolve().parent.parent.parent
        db_path = (base_dir / configured_path).resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_sqlite_checkpointer() -> SqliteSaver:
    """
    Create and return SqliteSaver checkpoint manager.
    """
    db_path = get_memory_db_path()
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)
    # Ensure tables are setup
    checkpointer.setup()
    return checkpointer
