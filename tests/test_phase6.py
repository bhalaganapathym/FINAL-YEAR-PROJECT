"""
Phase 6 automated tests: SQL Safety, SQL Validation Agent, and Execution Engine.
"""

import pytest
from app.utils.sql_safety import sanitize_and_check_sql_safety
from app.agents.validation_agent import SQLValidationAgent, ValidationResult
from app.database.executor import SQLExecutor, ExecutionResult


def test_sql_safety_valid_queries():
    """Verify that legitimate read-only queries pass security checks."""
    valid_queries = [
        "SELECT * FROM sales;",
        "SELECT r.region_name, SUM(s.revenue) FROM sales s JOIN regions r USING(region_id) GROUP BY r.region_name;",
        "WITH monthly_cte AS (SELECT month, SUM(revenue) AS rev FROM sales WHERE year=2024 GROUP BY month) SELECT * FROM monthly_cte;",
    ]
    for q in valid_queries:
        is_safe, reasons = sanitize_and_check_sql_safety(q)
        assert is_safe is True, f"Query incorrectly flagged unsafe: {q} -> {reasons}"


def test_sql_safety_blocks_dml_and_ddl():
    """Verify that dangerous queries containing DML/DDL keywords are rejected."""
    dangerous_queries = [
        "DROP TABLE customers;",
        "DELETE FROM orders WHERE order_id = 5;",
        "INSERT INTO regions (region_name) VALUES ('Test');",
        "UPDATE employees SET salary = 999999;",
        "TRUNCATE TABLE sales;",
        "ALTER TABLE products ADD COLUMN secret VARCHAR(50);",
        "WITH malicious_cte AS (DELETE FROM customers WHERE customer_id = 1) SELECT 1;",
        "SELECT * FROM sales; DROP TABLE users;",
    ]
    for q in dangerous_queries:
        is_safe, reasons = sanitize_and_check_sql_safety(q)
        assert is_safe is False, f"Dangerous query was NOT blocked: {q}"
        assert len(reasons) > 0


def test_validation_agent_rejects_nonexistent_tables():
    """Verify that queries referencing non-existent tables fail validation."""
    query = "SELECT * FROM non_existent_table_xyz JOIN customers USING(id);"
    result: ValidationResult = SQLValidationAgent.validate_sql(query)

    assert result.is_valid is False
    assert any("non_existent_table_xyz" in err for err in result.errors)


def test_sql_executor_successful_run():
    """Verify that SQLExecutor executes query, handles Decimals, and profiles latency."""
    query = "SELECT region_name, COUNT(*) AS cnt FROM regions GROUP BY region_name;"
    res: ExecutionResult = SQLExecutor.execute(query)

    assert res.success is True
    assert res.row_count == 4
    assert "region_name" in res.columns
    assert "cnt" in res.columns
    assert res.execution_time_ms > 0
    assert isinstance(res.data[0]["cnt"], int)


def test_sql_executor_handles_syntax_errors():
    """Verify that SQLExecutor catches database errors without crashing."""
    broken_query = "SELECT FROM WHERE;"
    res: ExecutionResult = SQLExecutor.execute(broken_query)

    assert res.success is False
    assert res.error_message is not None
    assert len(res.data) == 0
