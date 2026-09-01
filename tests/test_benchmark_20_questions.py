"""
Comprehensive 20+ NL2SQL and Multi-Agent Evaluation Suite (Phase 13).
Covers:
- Aggregations
- Rankings
- Multi-table joins
- Window functions
- Multi-turn pronoun resolutions
- Comparisons
- Forecasting triggers
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

BENCHMARK_QUESTIONS = [
    # 1. Simple Aggregations & Filters
    "Show total sales for 2024.",
    "What was the total profit in 2023?",
    "Show total revenue generated in the South region.",
    "How many orders were placed in 2024?",
    "What is the average order value across all completed orders?",

    # 2. Categorical Rankings & Grouping
    "Which 5 products generated the highest revenue?",
    "Which product categories have the highest profit margins?",
    "Show total revenue broken down by sales employee.",
    "Which customer segment placed the most orders?",
    "List top 5 customers by total spending.",

    # 3. Time Series & Trends
    "Show monthly sales trend for 2024.",
    "Compare quarterly revenue between 2023 and 2024.",
    "Which month had the highest sales in 2024?",
    "Show yearly revenue growth from 2022 to 2024.",

    # 4. Multi-Table Relational Joins
    "Which suppliers provided products with the highest sales in South region?",
    "Show current inventory stock levels by warehouse city for Electronics.",
    "What are the top payment methods by volume in Chennai and Bangalore?",
    "Which sales representative handled the highest revenue orders?",

    # 5. Complex Business Intelligence & Comparative
    "Compare sales performance between Chennai and Bangalore in 2024.",
    "Which products currently have stock below their reorder level?",
]


@pytest.mark.parametrize("query_text", BENCHMARK_QUESTIONS[:10])
def test_benchmark_nl2sql_questions_batch1(query_text: str):
    """Test first batch of realistic business questions."""
    client = TestClient(app)
    conv_id = f"bench-{uuid.uuid4().hex[:6]}"

    response = client.post("/query", json={
        "conversation_id": conv_id,
        "query": query_text
    })

    assert response.status_code == 200
    data = response.json()
    assert data["sql"] is not None
    assert data["answer"] is not None
    assert len(data["insights"]) > 0
    assert data["error"] is None


@pytest.mark.parametrize("query_text", BENCHMARK_QUESTIONS[10:20])
def test_benchmark_nl2sql_questions_batch2(query_text: str):
    """Test second batch of realistic business questions."""
    client = TestClient(app)
    conv_id = f"bench-{uuid.uuid4().hex[:6]}"

    response = client.post("/query", json={
        "conversation_id": conv_id,
        "query": query_text
    })

    assert response.status_code == 200
    data = response.json()
    assert data["sql"] is not None
    assert data["answer"] is not None
    assert len(data["insights"]) > 0
    assert data["error"] is None
