"""
Phase 5 Verification Script: Intent Agent & SQL Generation Agent.
Tests:
1. IntentAgent classification and multi-turn context resolution
2. SQLGenerationAgent natural language to MySQL query generation
3. Verifies generated SQL against live MySQL database
"""

import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from sqlalchemy import text
from app.database.connection import engine
from app.database.schema_loader import SchemaLoader
from app.agents.intent_agent import IntentAgent, IntentOutput
from app.agents.schema_agent import SchemaAgent, SchemaAgentResult
from app.agents.sql_agent import SQLGenerationAgent, SQLGenerationOutput

print("==================================================")
print("  PHASE 5 VERIFICATION: INTENT & SQL AGENTS       ")
print("==================================================")

schema = SchemaLoader.load_schema()

test_cases = [
    {
        "name": "Aggregation Query",
        "query": "Show total sales and profit by region for 2024.",
        "history": None,
    },
    {
        "name": "Top Products Ranking Query",
        "query": "Which 5 products generated the highest revenue?",
        "history": None,
    },
    {
        "name": "Follow-Up Context Resolution Query",
        "query": "What about for Chennai only?",
        "history": [
            {"role": "user", "content": "Show total sales by product category in 2024", "sql": "SELECT c.category_name, SUM(s.revenue) FROM sales s JOIN products p ON s.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id WHERE s.year = 2024 GROUP BY c.category_name;"},
            {"role": "assistant", "content": "Electronics was highest with 2.5 Cr."}
        ],
    },
    {
        "name": "Forecasting Intent Query",
        "query": "Forecast monthly sales for the next 6 months.",
        "history": None,
    }
]

with engine.connect() as conn:
    for idx, tc in enumerate(test_cases, 1):
        print(f"\n--> Test Case {idx}: {tc['name']}")
        print(f"    Input Query: \"{tc['query']}\"")

        # 1. Intent Classification
        intent: IntentOutput = IntentAgent.classify_intent(
            user_query=tc["query"],
            conversation_history=tc["history"]
        )
        print(f"    Intent: {intent.intent} | Metric: {intent.primary_metric} | Viz: {intent.visualization_required} | Forecast: {intent.forecast_required}")
        print(f"    Resolved Query: \"{intent.resolved_query}\"")

        # 2. Schema Selection
        schema_ctx: SchemaAgentResult = SchemaAgent.select_schema_context(
            user_query=intent.resolved_query,
            schema=schema
        )
        print(f"    Selected Tables: {schema_ctx.relevant_tables}")

        # 3. SQL Generation
        sql_out: SQLGenerationOutput = SQLGenerationAgent.generate_sql(
            user_query=intent.resolved_query,
            serialized_schema=schema_ctx.serialized_schema,
            intent_info=intent.model_dump(),
        )
        print(f"    Generated SQL:\n    {sql_out.sql}")

        # 4. Live DB Execution Check
        try:
            res = conn.execute(text(sql_out.sql))
            rows = res.fetchall()
            headers = list(res.keys())
            print(f"    [PASS] Executed successfully: {len(rows)} rows returned. Columns: {headers}")
            if rows:
                print(f"    Sample Row: {dict(zip(headers, rows[0]))}")
        except Exception as e:
            print(f"    [FAIL] SQL execution failed: {e}")
            raise e

print("\n=== PHASE 5 VERIFICATION COMPLETE: ALL CHECKS PASSED ===")
