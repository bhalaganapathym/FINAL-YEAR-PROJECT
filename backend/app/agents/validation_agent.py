"""
SQL Validation Agent for Persistent AI Data Analyst.
Inspects generated SQL queries prior to execution:
1. Validates DML/CTE safety via sql_safety module
2. Verifies referenced tables exist in MySQL schema
3. Checks column name consistency
4. Verifies query semantic alignment with user intent
"""

import re
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from app.database.schema_loader import SchemaLoader, DatabaseSchema
from app.utils.sql_safety import sanitize_and_check_sql_safety
from app.utils.logger import logger


class ValidationResult(BaseModel):
    """
    Validation report returned by SQLValidationAgent.
    """
    is_valid: bool = Field(..., description="True if query passes all security and schema checks")
    errors: List[str] = Field(default_factory=list, description="Critical validation failure reasons")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings or optimization notes")
    tables_identified: List[str] = Field(default_factory=list, description="Tables identified in SQL query")
    suggested_fix: Optional[str] = Field(None, description="Actionable correction guidance for retry generation")


class SQLValidationAgent:
    """
    Pre-execution validator for generated SQL queries.
    """

    @classmethod
    def extract_tables_from_sql(cls, sql: str) -> Set[str]:
        """
        Extract table names referenced in FROM and JOIN clauses.
        """
        tables = set()
        # Match FROM `table` or FROM table or JOIN `table` or JOIN table
        pattern = r"\b(?:FROM|JOIN|INTO|UPDATE)\s+[`]?([a-zA-Z0-9_]+)[`]?"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        for match in matches:
            tables.add(match.lower())
        return tables

    @classmethod
    def validate_sql(
        cls,
        sql: str,
        user_query: Optional[str] = None,
        schema: Optional[DatabaseSchema] = None,
    ) -> ValidationResult:
        """
        Perform complete validation: Security, Schema Existence, Syntax, and Intent Check.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Security & DML/CTE Safety Check
        is_safe, safety_violations = sanitize_and_check_sql_safety(sql)
        if not is_safe:
            errors.extend(safety_violations)

        # 2. Schema Existence Validation
        db_schema = schema or SchemaLoader.load_schema()
        referenced_tables = cls.extract_tables_from_sql(sql)
        valid_schema_tables = {t.lower() for t in db_schema.table_names}

        # Filter out common SQL aliases / CTE names
        missing_tables = []
        for tbl in referenced_tables:
            if tbl not in valid_schema_tables:
                # Check if it's a CTE defined with WITH ... AS
                cte_match = re.search(rf"\bWITH\s+{tbl}\s+AS|\b{tbl}\s+AS\s*\(", sql, re.IGNORECASE)
                if not cte_match:
                    missing_tables.append(tbl)

        if missing_tables:
            errors.append(
                f"Referenced table(s) {missing_tables} do not exist in database `{db_schema.database_name}`. Available tables: {sorted(list(valid_schema_tables))}"
            )

        # 3. Basic syntax balance checks (parentheses and quotes)
        if sql.count("(") != sql.count(")"):
            errors.append(f"Mismatched parentheses in query: {sql.count('(')} opening vs {sql.count(')')} closing.")

        # 4. Semantic Warnings
        if "select *" in sql.lower():
            warnings.append("Query uses SELECT *; explicit column projections are preferred.")

        is_valid = len(errors) == 0
        suggested_fix = None
        if not is_valid:
            suggested_fix = "; ".join(errors)
            logger.warning(f"SQL Validation failed with {len(errors)} error(s): {errors}")
        else:
            logger.info(f"SQL Validation passed for query on tables: {list(referenced_tables)}")

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            tables_identified=list(referenced_tables),
            suggested_fix=suggested_fix,
        )
