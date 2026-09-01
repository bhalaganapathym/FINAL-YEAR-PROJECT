"""
Automated End-to-End Tests for LangGraph Workflow, Memory, Visualization, Insights, and Forecasting (Phases 7-11).
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.graph.workflow import analytics_graph
from app.memory.checkpoint import get_sqlite_checkpointer


def test_langgraph_end_to_end_query():
    """Verify that a standard analytics question runs through the entire LangGraph multi-agent pipeline."""
    client = TestClient(app)
    conv_id = f"test-session-{uuid.uuid4().hex[:8]}"

    payload = {
        "conversation_id": conv_id,
        "query": "Show total sales and profit by product category in 2024."
    }

    response = client.post("/query", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["conversation_id"] == conv_id
    assert data["sql"] is not None
    assert len(data["data"]) > 0
    assert len(data["insights"]) > 0
    assert data["visualization"] is not None
    assert data["visualization"]["type"] in ["bar", "pie", "line"]
    assert data["execution_time_ms"] > 0


def test_langgraph_multi_turn_conversational_memory():
    """Verify that multi-turn follow-up queries use SQLite checkpoint memory."""
    client = TestClient(app)
    conv_id = f"test-multi-turn-{uuid.uuid4().hex[:8]}"

    # Turn 1
    t1_res = client.post("/query", json={
        "conversation_id": conv_id,
        "query": "Show total sales by region in 2024."
    })
    assert t1_res.status_code == 200
    assert len(t1_res.json()["data"]) == 4

    # Turn 2: Follow-up modifying previous query
    t2_res = client.post("/query", json={
        "conversation_id": conv_id,
        "query": "What about for Chennai only?"
    })
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    assert t2_data["sql"] is not None
    assert "chennai" in t2_data["sql"].lower() or "chennai" in t2_data["answer"].lower()

    # Check conversation history endpoint
    hist_res = client.get(f"/conversation/{conv_id}")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history["messages"]) >= 4  # 2 user + 2 assistant


def test_langgraph_forecasting_pipeline():
    """Verify that predictive forecasting queries trigger the Forecast Agent and return prediction cones."""
    client = TestClient(app)
    conv_id = f"test-forecast-{uuid.uuid4().hex[:8]}"

    payload = {
        "conversation_id": conv_id,
        "query": "Forecast monthly revenue for the next 6 months."
    }

    response = client.post("/query", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["forecast"] is not None
    assert len(data["forecast"]["predictions"]) == 6
    assert data["forecast"]["figure"] is not None
    assert "confidence_intervals" in data["forecast"]
