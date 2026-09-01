"""
Database Management and Upload API Routes.
Provides endpoints for:
- Uploading SQLite, CSV, Excel, and SQL files
- Connecting to custom remote databases
- Inspecting schemas of uploaded datasets
"""

from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from app.database.session_manager import DatabaseSessionManager, DatabaseSourceInfo
from app.database.schema_loader import SchemaLoader
from app.services.ingestion_service import IngestionService
from app.utils.logger import logger

router = APIRouter(prefix="/database", tags=["Database Management"])


class ConnectDatabaseRequest(BaseModel):
    """
    Request model for connecting to a remote database URI.
    """
    uri: str = Field(..., description="SQLAlchemy database connection string (e.g. mysql+pymysql://user:pass@host/db)")
    name: Optional[str] = Field(None, description="Optional custom display name for this connection")


@router.post("/upload", response_model=DatabaseSourceInfo, status_code=status.HTTP_201_CREATED)
async def upload_database_file(
    file: UploadFile = File(...)
) -> DatabaseSourceInfo:
    """
    Upload and mount a database or spreadsheet (.db, .sqlite, .csv, .xlsx, .sql).
    Automatically parses schema, creates relational tables, and returns database_id.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    logger.info(f"Received file upload: '{file.filename}' ({file.content_type})")

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Max 50MB
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file exceeds 50MB limit.")

        info = IngestionService.ingest_file(filename=file.filename, content=content)
        return info

    except ValueError as ve:
        logger.warning(f"File validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to ingest file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")


@router.post("/connect", response_model=DatabaseSourceInfo, status_code=status.HTTP_200_OK)
async def connect_remote_database(
    request: ConnectDatabaseRequest
) -> DatabaseSourceInfo:
    """
    Connect to a remote MySQL, PostgreSQL, or SQLite database via connection URI.
    """
    try:
        info = IngestionService.connect_uri(uri=request.uri, name=request.name)
        return info
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=400, detail=f"Could not connect to database URI: {str(e)}")


@router.get("/list", response_model=List[DatabaseSourceInfo])
async def list_databases() -> List[DatabaseSourceInfo]:
    """
    List all available database sources (default MySQL and user-uploaded datasets).
    """
    return DatabaseSessionManager.list_sources()


@router.get("/{database_id}/schema")
async def get_database_schema(database_id: str):
    """
    Get introspected schema for a specific database.
    """
    try:
        schema = SchemaLoader.load_schema(database_id=database_id)
        meta = DatabaseSessionManager.get_metadata(database_id)
        return {
            "database_id": database_id,
            "metadata": meta.model_dump() if meta else None,
            "tables": {t: info.model_dump() for t, info in schema.tables.items()},
        }
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(status_code=404, detail=f"Database '{database_id}' schema not found: {str(e)}")
