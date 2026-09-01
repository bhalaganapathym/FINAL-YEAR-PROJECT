"""
Dynamic MySQL and SQLite Schema Introspection Module.
Extracts tables, columns, data types, primary keys, foreign keys, and row counts
via SQLAlchemy reflection across any active database engine.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from sqlalchemy import inspect, text, Engine
from app.database.connection import engine as default_engine
from app.database.session_manager import DatabaseSessionManager
from app.utils.logger import logger


class ColumnInfo(BaseModel):
    """
    Detailed information for a single table column.
    """
    name: str
    data_type: str
    nullable: bool = True
    default: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_target: Optional[str] = None  # e.g., 'regions.region_id'
    comment: Optional[str] = None


class TableInfo(BaseModel):
    """
    Metadata representation for a single database table.
    """
    name: str
    columns: Dict[str, ColumnInfo] = Field(default_factory=dict)
    primary_keys: List[str] = Field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = Field(default_factory=list)
    row_count: Optional[int] = None
    comment: Optional[str] = None

    @property
    def column_names(self) -> List[str]:
        return list(self.columns.keys())


class DatabaseSchema(BaseModel):
    """
    Complete introspected database schema representation.
    """
    database_name: str
    tables: Dict[str, TableInfo] = Field(default_factory=dict)

    @property
    def table_names(self) -> List[str]:
        return list(self.tables.keys())

    def get_table(self, table_name: str) -> Optional[TableInfo]:
        return self.tables.get(table_name.lower())


class SchemaLoader:
    """
    Introspects relational database schemas dynamically via SQLAlchemy 2.0 reflection.
    """

    @classmethod
    def load_schema(
        cls,
        target_engine: Optional[Engine] = None,
        database_id: Optional[str] = None,
    ) -> DatabaseSchema:
        """
        Dynamically inspect all tables, columns, keys, and row counts from target database.
        """
        eng = target_engine or DatabaseSessionManager.get_engine(database_id)
        inspector = inspect(eng)

        db_name = "sqlite_db" if eng.name == "sqlite" else (eng.url.database or "database")
        db_schema = DatabaseSchema(database_name=db_name)

        table_names = inspector.get_table_names()
        logger.info(f"Dynamically introspecting {len(table_names)} tables from database '{db_name}'...")

        with eng.connect() as conn:
            for tbl_name in table_names:
                table_info = TableInfo(name=tbl_name)

                # 1. Fetch Primary Keys
                pk_constraint = inspector.get_pk_constraint(tbl_name)
                if pk_constraint and "constrained_columns" in pk_constraint:
                    table_info.primary_keys = pk_constraint["constrained_columns"]

                # 2. Fetch Foreign Keys
                fk_constraints = inspector.get_foreign_keys(tbl_name)
                for fk in fk_constraints:
                    referred_table = fk.get("referred_table", "")
                    referred_columns = fk.get("referred_columns", [])
                    constrained_columns = fk.get("constrained_columns", [])

                    for src_col, target_col in zip(constrained_columns, referred_columns):
                        table_info.foreign_keys.append({
                            "column": src_col,
                            "references": f"{referred_table}.{target_col}",
                        })

                # 3. Fetch Columns
                columns = inspector.get_columns(tbl_name)
                for col in columns:
                    col_name = col["name"]
                    is_pk = col_name in table_info.primary_keys

                    fk_target = None
                    for fk in table_info.foreign_keys:
                        if fk["column"] == col_name:
                            fk_target = fk["references"]
                            break

                    col_info = ColumnInfo(
                        name=col_name,
                        data_type=str(col["type"]),
                        nullable=col.get("nullable", True),
                        default=str(col.get("default", "")) if col.get("default") is not None else None,
                        is_primary_key=is_pk,
                        is_foreign_key=fk_target is not None,
                        foreign_key_target=fk_target,
                        comment=col.get("comment"),
                    )
                    table_info.columns[col_name] = col_info

                # 4. Fetch Approximate/Exact Row Count
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM `{tbl_name}`" if eng.name != "sqlite" else f'SELECT COUNT(*) FROM "{tbl_name}"')).scalar()
                    table_info.row_count = count_result
                except Exception as e:
                    logger.warning(f"Could not count rows for table {tbl_name}: {e}")
                    table_info.row_count = 0

                db_schema.tables[tbl_name.lower()] = table_info

        return db_schema

    @classmethod
    def serialize_schema(
        cls,
        schema: DatabaseSchema,
        included_tables: Optional[Set[str]] = None,
    ) -> str:
        """
        Serialize schema information into compact, LLM-friendly DDL definitions.
        """
        ddl_parts = []
        tables_to_include = included_tables if included_tables is not None else set(schema.tables.keys())

        for tbl_name, tbl_info in schema.tables.items():
            if tbl_name.lower() not in [t.lower() for t in tables_to_include]:
                continue

            col_defs = []
            for col in tbl_info.columns.values():
                flags = []
                if col.is_primary_key:
                    flags.append("PRIMARY KEY")
                if col.is_foreign_key and col.foreign_key_target:
                    flags.append(f"REFERENCES {col.foreign_key_target}")
                if not col.nullable and not col.is_primary_key:
                    flags.append("NOT NULL")

                flag_str = f" ({', '.join(flags)})" if flags else ""
                col_defs.append(f"  - `{col.name}`: {col.data_type}{flag_str}")

            row_info = f" | ~{tbl_info.row_count} rows" if tbl_info.row_count is not None else ""
            table_block = (
                f"TABLE `{tbl_info.name}`{row_info}:\n"
                f"COLUMNS:\n" + "\n".join(col_defs)
            )
            ddl_parts.append(table_block)

        return "\n\n".join(ddl_parts)
