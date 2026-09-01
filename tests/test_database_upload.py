"""
Unit and Integration Tests for Database & Spreadsheet Uploads.
"""

import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_csv_database():
    """Verify that a CSV upload is converted to a relational database and can be queried."""
    # Create sample CSV in memory
    csv_data = (
        "employee_id,name,department,salary,join_year\n"
        "101,John Doe,Engineering,95000,2021\n"
        "102,Jane Smith,Marketing,82000,2022\n"
        "103,Bob Wilson,Engineering,115000,2020\n"
        "104,Alice Brown,Finance,91000,2023\n"
    ).encode("utf-8")

    files = {"file": ("company_staff.csv", io.BytesIO(csv_data), "text/csv")}
    res = client.post("/database/upload", files=files)

    assert res.status_code == 201
    db_info = res.json()
    assert db_info["database_id"].startswith("db_")
    assert db_info["source_type"] == "csv"
    assert "company_staff" in db_info["tables"]

    # Verify query executes on uploaded CSV database
    q_res = client.post("/query", json={
        "query": "Which employee has the highest salary?",
        "database_id": db_info["database_id"],
    })

    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["sql"] is not None
    assert "company_staff" in q_data["sql"].lower()
    assert len(q_data["data"]) > 0


def test_list_databases_endpoint():
    """Verify that /database/list returns available sources."""
    res = client.get("/database/list")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 1
    assert any(s["database_id"] == "default" for s in sources)
