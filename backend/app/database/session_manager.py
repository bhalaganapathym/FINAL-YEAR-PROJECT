"""
Database Session Manager for Multi-Source & User Uploaded Databases.
Manages isolated SQLAlchemy engines and schemas per database ID.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import Engine
from pydantic import BaseModel, Field
from app.database.connection import engine as default_mysql_engine
from app.utils.logger import logger


class DatabaseSourceInfo(BaseModel):
    """
    Metadata about an active data source.
    """
    database_id: str
    name: str
    source_type: str = Field(..., description="'mysql', 'sqlite', 'csv', 'excel', 'sql_dump', 'custom_uri'")
    tables_count: int = 0
    tables: List[str] = Field(default_factory=list)
    created_at: str
    file_path: Optional[str] = None
    is_default: bool = False


class DatabaseSessionManager:
    """
    Registry for isolated SQLAlchemy database connections.
    """
    _engines: Dict[str, Engine] = {}
    _metadata: Dict[str, DatabaseSourceInfo] = {}

    @classmethod
    def get_upload_dir(cls) -> Path:
        """
        Get or create base directory for user uploaded database files.
        """
        upload_dir = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    @classmethod
    def register_engine(
        cls,
        database_id: str,
        engine: Engine,
        info: DatabaseSourceInfo
    ):
        """
        Register a new database engine and its metadata.
        """
        cls._engines[database_id] = engine
        cls._metadata[database_id] = info
        logger.info(f"Registered database source '{info.name}' (ID: {database_id}, Type: {info.source_type}, Tables: {len(info.tables)})")

    @classmethod
    def get_engine(cls, database_id: Optional[str] = None) -> Engine:
        """
        Retrieve database engine by ID. Defaults to standard MySQL engine if database_id is None.
        """
        if not database_id or database_id == "default" or database_id not in cls._engines:
            return default_mysql_engine
        return cls._engines[database_id]

    @classmethod
    def get_metadata(cls, database_id: Optional[str] = None) -> Optional[DatabaseSourceInfo]:
        """
        Get database source metadata.
        """
        if not database_id or database_id == "default":
            return DatabaseSourceInfo(
                database_id="default",
                name="Default MySQL (Business Analytics)",
                source_type="mysql",
                tables_count=11,
                tables=["categories", "customers", "employees", "inventory", "order_items", "orders", "payments", "products", "regions", "sales", "suppliers"],
                created_at="Initial Seed",
                is_default=True,
            )
        return cls._metadata.get(database_id)

    @classmethod
    def list_sources(cls) -> List[DatabaseSourceInfo]:
        """
        List all available database sources (default + user uploaded).
        """
        sources = [cls.get_metadata("default")]
        for d_id, meta in cls._metadata.items():
            sources.append(meta)
        return sources
