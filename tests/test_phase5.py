"""
Phase 5 automated tests: Intent classification and SQL generation.
"""

import pytest
from sqlalchemy import text
from app.database.connection import engine
from app.database.schema_loader import SchemaLoader
from app.agents.intent_agent import IntentAgent
from app.agents.schema_agent import SchemaAgent
from app.agents.sql_agent import SQLGenerationAgent


def test_intent_classification_simple():
    """Verify that intent is classified as aggregation for sum queries."""
    query = "Show total revenue by region in 2024"
    intent = IntentAgent.classify_intent(query)

    assert intent.intent in ["aggregation", "trend", "ranking"]
    assert intent.visualization_required is True
    assert "2024" in str(intent.time_range) or "2024" in intent.resolved_query


def test_intent_follow_up_resolution():
    """Verify pronoun and context resolution in multi-turn conversation."""
    history = [
        {"role": "user", "content": "Show sales by category in 2024", "sql": "SELECT category_name, SUM(revenue) FROM sales JOIN products USING(product_id) JOIN categories USING(category_id) WHERE year = 2024 GROUP BY category_name;"},
        {"role": "assistant", "content": "Computers & Laptops was top with 1.8 Cr."}
    ]
    query = "What about for Chennai only?"
    intent = IntentAgent.classify_intent(query, conversation_history=history)

    assert "chennai" in intent.resolved_query.lower()
    assert "category" in intent.resolved_query.lower() or "2024" in intent.resolved_query


def test_sql_generation_and_execution():
    """Verify end-to-end SQL generation and successful execution against MySQL."""
    schema = SchemaLoader.load_schema()
    query = "What are the top 3 highest revenue product categories?"

    intent = IntentAgent.classify_intent(query)
    schema_ctx = SchemaAgent.select_schema_context(intent.resolved_query, schema=schema)
    sql_out = SQLGenerationAgent.generate_sql(
        user_query=intent.resolved_query,
        serialized_schema=schema_ctx.serialized_schema,
        intent_info=intent.model_dump(),
    )

    assert sql_out.sql.lower().startswith("select") or sql_out.sql.lower().startswith("with")
    assert "limit" in sql_out.sql.lower() or "top" in sql_out.sql.lower() or "order by" in sql_out.sql.lower()

    with engine.connect() as conn:
        res = conn.execute(text(sql_out.sql))
        rows = res.fetchall()
        assert len(rows) > 0
        assert len(rows) <= 3
