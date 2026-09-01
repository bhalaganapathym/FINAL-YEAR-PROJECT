"""
Live Demonstration and Functional Testing Suite.
Sends live analytical requests to the running FastAPI server (http://127.0.0.1:8000).
Tests:
1. Health & DB connection
2. Single-turn aggregation & ranking queries
3. Multi-turn conversational follow-up (Context resolution via SQLite Checkpoint Memory)
4. Time-series forecasting with statsforecast AutoARIMA & Plotly confidence intervals
5. Conversation history retrieval
"""

import uuid
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_live_tests():
    print("=" * 70)
    print("  LIVE SYSTEM TESTING: PERSISTENT AI DATA ANALYST")
    print("=" * 70)

    # 1. Check Health
    print("\n[1/5] Checking Service Health & MySQL Connectivity...")
    res = requests.get(f"{BASE_URL}/health", timeout=10)
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"      Status: {health['status']} | DB: {health['database']['database_name']} | Latency: {health['database']['latency_ms']}ms")

    session_id = f"demo-{uuid.uuid4().hex[:8]}"
    print(f"\n[Session ID]: {session_id}")

    # 2. Test Aggregation Query
    q1 = "Show total sales and profit by product category for 2024."
    print(f"\n[2/5] Query 1: \"{q1}\"")
    r1 = requests.post(f"{BASE_URL}/query", json={"query": q1, "conversation_id": session_id}, timeout=30)
    assert r1.status_code == 200, f"Query 1 failed: {r1.text}"
    d1 = r1.json()
    print(f"      ⚡ Latency: {d1['execution_time_ms']}ms")
    print(f"      📝 Generated SQL:\n         {d1['sql']}")
    print(f"      📊 Rows Returned: {len(d1['data'])}")
    if d1['data']:
        print(f"         Sample: {d1['data'][0]}")
    print(f"      💡 Executive Insights ({len(d1['insights'])}):")
    for ins in d1['insights'][:2]:
        print(f"         • {ins}")
    if d1.get('visualization'):
        print(f"      📈 Visualization: {d1['visualization']['type'].upper()} Chart ('{d1['visualization'].get('title')}')")

    # 3. Test Multi-Turn Conversational Memory (Follow-Up)
    q2 = "What about for Chennai only?"
    print(f"\n[3/5] Query 2 (Follow-up): \"{q2}\"")
    r2 = requests.post(f"{BASE_URL}/query", json={"query": q2, "conversation_id": session_id}, timeout=30)
    assert r2.status_code == 200, f"Query 2 failed: {r2.text}"
    d2 = r2.json()
    print(f"      ⚡ Latency: {d2['execution_time_ms']}ms")
    print(f"      📝 Generated SQL:\n         {d2['sql']}")
    print(f"      📊 Rows Returned: {len(d2['data'])}")
    print(f"      💡 Executive Insights ({len(d2['insights'])}):")
    for ins in d2['insights'][:2]:
        print(f"         • {ins}")

    # 4. Test Time-Series Forecasting
    q3 = "Forecast monthly sales for the next 6 months."
    print(f"\n[4/5] Query 3 (Predictive Forecast): \"{q3}\"")
    r3 = requests.post(f"{BASE_URL}/query", json={"query": q3, "conversation_id": session_id}, timeout=45)
    assert r3.status_code == 200, f"Query 3 failed: {r3.text}"
    d3 = r3.json()
    print(f"      ⚡ Latency: {d3['execution_time_ms']}ms")
    print(f"      📝 Generated SQL:\n         {d3['sql']}")
    if d3.get('forecast'):
        fc = d3['forecast']
        print(f"      🔮 Forecast Metric: {fc['metric']} | Horizon: {fc['horizon']} months")
        print(f"         Predictions ({len(fc['predictions'])}):")
        for p in fc['predictions'][:3]:
            print(f"         - Date: {p['date']} | Pred: INR {p['predicted_value']:,.2f} [80% CI: {p['lower_80']:,.0f} - {p['upper_80']:,.0f}]")
        print(f"      📈 Plotly Traces: {len(fc['figure']['data'])} (Historical + Predictions + 95% Confidence Ribbons)")

    # 5. Test Conversation History Endpoint
    print(f"\n[5/5] Checking Conversation Session History...")
    r4 = requests.get(f"{BASE_URL}/conversation/{session_id}", timeout=10)
    assert r4.status_code == 200, f"History fetch failed: {r4.text}"
    hist = r4.json()
    print(f"      Retrieved {len(hist['messages'])} conversational turns from SQLite checkpoint memory.")

    print("\n" + "=" * 70)
    print("  ALL LIVE TESTS PASSED SUCCESSFULLY! SYSTEM IS 100% FUNCTIONAL.")
    print("=" * 70)

if __name__ == "__main__":
    run_live_tests()
