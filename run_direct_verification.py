"""
Direct TestClient Runner for End-to-End Verification.
Runs directly through FastAPI TestClient with ASCII output formatting.
"""

import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app

def run_direct_verification():
    print("=" * 70)
    print("  E2E DIRECT SYSTEM VERIFICATION: PERSISTENT AI DATA ANALYST")
    print("=" * 70)

    client = TestClient(app)

    # 1. Health Endpoint
    print("\n[1/4] Checking Service Health & Database Connection...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"      Status: {health['status']} | DB: {health['database']['database_name']} | Latency: {health['database']['latency_ms']}ms")

    session_id = f"test-run-{uuid.uuid4().hex[:8]}"
    print(f"\n[Session ID]: {session_id}")

    # 2. Aggregation Query
    q1 = "Show total sales and profit by product category for 2024."
    print(f"\n[2/4] Query 1 (Aggregation & Ranking): \"{q1}\"")
    r1 = client.post("/query", json={"query": q1, "conversation_id": session_id})
    assert r1.status_code == 200, f"Query 1 failed: {r1.text}"
    d1 = r1.json()
    print(f"      [LATENCY]: {d1['execution_time_ms']}ms")
    print(f"      [SQL]:\n{d1['sql']}")
    print(f"      [ROWS RETURNED]: {len(d1['data'])}")
    if d1['data']:
        print(f"      [SAMPLE ROW]: {d1['data'][0]}")
    print(f"      [EXECUTIVE INSIGHTS] ({len(d1['insights'])}):")
    for ins in d1['insights'][:2]:
        print(f"      * {ins}")
    if d1.get('visualization'):
        print(f"      [PLOTLY CHART]: {d1['visualization']['type'].upper()} ('{d1['visualization'].get('title')}')")

    # 3. Follow-Up Query (Persistent Memory Context Resolution)
    q2 = "What about for Chennai only?"
    print(f"\n[3/4] Query 2 (Conversational Follow-up): \"{q2}\"")
    r2 = client.post("/query", json={"query": q2, "conversation_id": session_id})
    assert r2.status_code == 200, f"Query 2 failed: {r2.text}"
    d2 = r2.json()
    print(f"      [LATENCY]: {d2['execution_time_ms']}ms")
    print(f"      [SQL]:\n{d2['sql']}")
    print(f"      [ROWS RETURNED]: {len(d2['data'])}")
    if d2['data']:
        print(f"      [SAMPLE ROW]: {d2['data'][0]}")

    # 4. Predictive Forecast Query
    q3 = "Forecast monthly sales for the next 6 months."
    print(f"\n[4/4] Query 3 (Time-Series Forecasting): \"{q3}\"")
    r3 = client.post("/query", json={"query": q3, "conversation_id": session_id})
    assert r3.status_code == 200, f"Query 3 failed: {r3.text}"
    d3 = r3.json()
    print(f"      [LATENCY]: {d3['execution_time_ms']}ms")
    print(f"      [SQL]:\n{d3['sql']}")
    if d3.get('forecast'):
        fc = d3['forecast']
        print(f"      [FORECAST METRIC]: {fc['metric']} | Horizon: {fc['horizon']} periods")
        print(f"      [PREDICTIONS]:")
        for p in fc['predictions'][:3]:
            print(f"      - {p['date']}: INR {p['predicted_value']:,.2f} [80% CI: {p['lower_80']:,.0f} - {p['upper_80']:,.0f}]")
        print(f"      [PLOTLY TRACES]: {len(fc['figure']['data'])}")

    print("\n" + "=" * 70)
    print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_direct_verification()
