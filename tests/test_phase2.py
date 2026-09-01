"""
Phase 2 automated tests: MySQL connectivity, SQLAlchemy pool, table existence, and data integrity.
"""

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import engine, test_db_connection as check_db_connection


def test_db_connection_direct():
    """Verify that SQLAlchemy engine connects to MySQL via PyMySQL."""
    success, msg, latency = check_db_connection()
    assert success is True
    assert "business_analytics" in msg
    assert latency > 0


def test_health_endpoint_with_db():
    """Verify that GET /health returns database connectivity status."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"]["connected"] is True
    assert data["database"]["database_name"] == "business_analytics"


def test_all_11_tables_exist():
    """Verify all 11 business tables exist in MySQL."""
    expected_tables = {
        "regions", "categories", "suppliers", "employees",
        "customers", "products", "inventory", "orders",
        "order_items", "payments", "sales"
    }

    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES;"))
        actual_tables = {row[0].lower() for row in result.fetchall()}

    missing = expected_tables - actual_tables
    assert not missing, f"Missing required tables: {missing}"


def test_seed_data_volume():
    """Verify that seed data meets the 3-year and 500+ order requirement for forecasting."""
    with engine.connect() as conn:
        order_count = conn.execute(text("SELECT COUNT(*) FROM orders;")).scalar()
        sales_count = conn.execute(text("SELECT COUNT(*) FROM sales;")).scalar()
        min_date, max_date = conn.execute(text("SELECT MIN(order_date), MAX(order_date) FROM orders;")).fetchone()

    assert order_count >= 500, f"Expected at least 500 orders, found {order_count}"
    assert sales_count >= 500, f"Expected at least 500 sales records, found {sales_count}"
    assert str(min_date).startswith("2022"), f"Expected 2022 start date, got {min_date}"
    assert str(max_date).startswith("2024"), f"Expected 2024 end date, got {max_date}"
