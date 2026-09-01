"""
Safe SQL Execution Engine for Persistent AI Data Analyst.
Executes validated read-only SQL queries with:
- Multi-source database engine resolution (MySQL or session uploaded SQLite/Postgres)
- Configurable statement timeout (QUERY_TIMEOUT)
- Row limit truncation (MAX_RESULT_ROWS)
- Type conversion (Decimal -> float/int, date/datetime -> ISO string)
- Execution time profiling
- Sanitized error reporting
"""

import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import text, Engine
from app.config import get_settings
from app.database.connection import engine as default_engine
from app.database.session_manager import DatabaseSessionManager
from app.utils.logger import logger

settings = get_settings()


class ExecutionResult(BaseModel):
    """
    Standardized result payload from SQL execution.
    """
    success: bool = Field(..., description="True if query executed without errors")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Row records formatted as JSON dicts")
    columns: List[str] = Field(default_factory=list, description="Column header names")
    row_count: int = Field(default=0, description="Total number of rows returned")
    execution_time_ms: float = Field(default=0.0, description="Query execution duration in milliseconds")
    error_message: Optional[str] = Field(None, description="Sanitized database error message if failed")
    is_truncated: bool = Field(default=False, description="True if rows exceeded MAX_RESULT_ROWS")


def serialize_value(val: Any) -> Any:
    """
    Convert database objects to JSON-serializable primitives.
    """
    if isinstance(val, Decimal):
        return float(val) if val % 1 != 0 else int(val)
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="ignore")
    return val


class SQLExecutor:
    """
    Executes validated SQL queries safely against MySQL or user-uploaded databases.
    """

    @classmethod
    def execute(
        cls,
        sql: str,
        max_rows: Optional[int] = None,
        timeout: Optional[int] = None,
        database_id: Optional[str] = None,
        target_engine: Optional[Engine] = None,
    ) -> ExecutionResult:
        """
        Execute validated query and return structured, sanitized result.
        """
        eng = target_engine or DatabaseSessionManager.get_engine(database_id)
        row_limit = max_rows or settings.MAX_RESULT_ROWS
        query_timeout = timeout or settings.QUERY_TIMEOUT
        start_time = time.time()

        clean_sql = sql.strip().rstrip(";")

        # Inject LIMIT if not already present to protect memory
        has_limit = "limit" in clean_sql.lower()
        effective_sql = clean_sql
        if not has_limit and not clean_sql.lower().startswith("show") and not clean_sql.lower().startswith("explain"):
            effective_sql = f"{clean_sql} LIMIT {row_limit + 1}"

        logger.info(f"Executing SQL on engine '{eng.name}': {effective_sql[:120]}... [timeout={query_timeout}s, max_rows={row_limit}]")

        try:
            with eng.connect() as conn:
                if eng.name == "mysql":
                    try:
                        conn.execute(text(f"SET SESSION max_execution_time = {query_timeout * 1000};"))
                    except Exception:
                        pass

                cursor_result = conn.execute(text(effective_sql))
                raw_rows = cursor_result.fetchall()
                columns = list(cursor_result.keys()) if cursor_result.keys() else []

            duration_ms = (time.time() - start_time) * 1000

            is_truncated = len(raw_rows) > row_limit
            final_rows = raw_rows[:row_limit]

            serialized_data: List[Dict[str, Any]] = []
            for row in final_rows:
                row_dict = {}
                for col_name, val in zip(columns, row):
                    row_dict[col_name] = serialize_value(val)
                serialized_data.append(row_dict)

            logger.info(f"Execution succeeded in {duration_ms:.2f}ms: returned {len(serialized_data)} rows.")

            return ExecutionResult(
                success=True,
                data=serialized_data,
                columns=columns,
                row_count=len(serialized_data),
                execution_time_ms=round(duration_ms, 2),
                error_message=None,
                is_truncated=is_truncated,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            err_str = str(e)
            logger.error(f"SQL Execution failed in {duration_ms:.2f}ms: {err_str}")

            if settings.DB_PASSWORD:
                err_str = err_str.replace(settings.DB_PASSWORD, "[REDACTED_PASSWORD]")

            return ExecutionResult(
                success=False,
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=round(duration_ms, 2),
                error_message=err_str,
                is_truncated=False,
            )
