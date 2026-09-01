"""
Database & Spreadsheet Ingestion Service.
Converts user-uploaded SQLite, CSV, Excel, and SQL dump files into isolated SQLAlchemy databases.
"""

import os
import re
import uuid
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import create_engine, inspect, text, Engine
from app.database.session_manager import DatabaseSessionManager, DatabaseSourceInfo
from app.utils.logger import logger


def sanitize_table_name(name: str) -> str:
    """
    Sanitize file or sheet name into a clean SQL table name.
    """
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip())
    clean = re.sub(r"_+", "_", clean).strip("_").lower()
    if not clean or clean[0].isdigit():
        clean = f"table_{clean}"
    return clean


def sanitize_column_name(name: str) -> str:
    """
    Sanitize dataframe column name into clean snake_case.
    """
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", str(name).strip())
    clean = re.sub(r"_+", "_", clean).strip("_").lower()
    return clean or "col"


class IngestionService:
    """
    Handles user file uploads and connection strings.
    """

    @classmethod
    def ingest_file(cls, filename: str, content: bytes) -> DatabaseSourceInfo:
        """
        Process uploaded database or spreadsheet and return registered metadata.
        """
        upload_dir = DatabaseSessionManager.get_upload_dir()
        db_id = f"db_{uuid.uuid4().hex[:10]}"
        session_folder = upload_dir / db_id
        session_folder.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix.lower()
        file_path = session_folder / filename
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Ingesting uploaded file '{filename}' ({len(content)} bytes) into session '{db_id}'")

        if ext in [".db", ".sqlite", ".sqlite3"]:
            return cls._ingest_sqlite_file(db_id, filename, file_path)
        elif ext == ".csv":
            return cls._ingest_csv_file(db_id, filename, file_path)
        elif ext in [".xlsx", ".xls"]:
            return cls._ingest_excel_file(db_id, filename, file_path)
        elif ext == ".sql":
            return cls._ingest_sql_dump(db_id, filename, file_path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: .db, .sqlite, .csv, .xlsx, .sql")

    @classmethod
    def _ingest_sqlite_file(cls, db_id: str, original_filename: str, file_path: Path) -> DatabaseSourceInfo:
        """
        Mount existing SQLite database file.
        """
        sqlite_url = f"sqlite:///{file_path.resolve()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

        # Introspect tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        info = DatabaseSourceInfo(
            database_id=db_id,
            name=original_filename,
            source_type="sqlite",
            tables_count=len(tables),
            tables=tables,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=str(file_path),
            is_default=False,
        )

        DatabaseSessionManager.register_engine(db_id, engine, info)
        return info

    @classmethod
    def _ingest_csv_file(cls, db_id: str, original_filename: str, file_path: Path) -> DatabaseSourceInfo:
        """
        Convert CSV file into a relational SQLite table with sanitized headers and typed columns.
        """
        table_name = sanitize_table_name(Path(original_filename).stem)
        sqlite_db_path = file_path.parent / "database.sqlite"
        sqlite_url = f"sqlite:///{sqlite_db_path.resolve()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

        # Read CSV with pandas
        df = pd.read_csv(file_path)
        df.columns = [sanitize_column_name(c) for c in df.columns]

        # Ingest into SQLite table
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

        info = DatabaseSourceInfo(
            database_id=db_id,
            name=original_filename,
            source_type="csv",
            tables_count=1,
            tables=[table_name],
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=str(sqlite_db_path),
            is_default=False,
        )

        DatabaseSessionManager.register_engine(db_id, engine, info)
        return info

    @classmethod
    def _ingest_excel_file(cls, db_id: str, original_filename: str, file_path: Path) -> DatabaseSourceInfo:
        """
        Convert Excel sheets into relational tables.
        """
        sqlite_db_path = file_path.parent / "database.sqlite"
        sqlite_url = f"sqlite:///{sqlite_db_path.resolve()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

        xls = pd.ExcelFile(file_path)
        tables = []

        for sheet_name in xls.sheet_names:
            tbl_name = sanitize_table_name(sheet_name)
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.columns = [sanitize_column_name(c) for c in df.columns]
            df.to_sql(tbl_name, con=engine, if_exists="replace", index=False)
            tables.append(tbl_name)

        info = DatabaseSourceInfo(
            database_id=db_id,
            name=original_filename,
            source_type="excel",
            tables_count=len(tables),
            tables=tables,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=str(sqlite_db_path),
            is_default=False,
        )

        DatabaseSessionManager.register_engine(db_id, engine, info)
        return info

    @classmethod
    def _ingest_sql_dump(cls, db_id: str, original_filename: str, file_path: Path) -> DatabaseSourceInfo:
        """
        Execute SQL schema and seed dump into isolated SQLite database.
        """
        sqlite_db_path = file_path.parent / "database.sqlite"
        sqlite_url = f"sqlite:///{sqlite_db_path.resolve()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sql_script = f.read()

        # Split and execute non-empty statements
        with engine.connect() as conn:
            for statement in sql_script.split(";"):
                stmt = statement.strip()
                if stmt:
                    try:
                        conn.execute(text(stmt))
                    except Exception as e:
                        logger.warning(f"Error executing statement in SQL dump: {e}")
            conn.commit()

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        info = DatabaseSourceInfo(
            database_id=db_id,
            name=original_filename,
            source_type="sql_dump",
            tables_count=len(tables),
            tables=tables,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=str(sqlite_db_path),
            is_default=False,
        )

        DatabaseSessionManager.register_engine(db_id, engine, info)
        return info

    @classmethod
    def connect_uri(cls, uri: str, name: Optional[str] = None) -> DatabaseSourceInfo:
        """
        Connect to a remote MySQL, PostgreSQL, or SQLite database by connection string.
        """
        db_id = f"db_{uuid.uuid4().hex[:10]}"
        engine = create_engine(uri)

        # Test connectivity
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        display_name = name or uri.split("@")[-1].split("?")[0]

        info = DatabaseSourceInfo(
            database_id=db_id,
            name=f"Connected: {display_name}",
            source_type="custom_uri",
            tables_count=len(tables),
            tables=tables,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=None,
            is_default=False,
        )

        DatabaseSessionManager.register_engine(db_id, engine, info)
        return info
