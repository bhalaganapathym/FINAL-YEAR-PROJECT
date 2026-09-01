"""
Phase 4 Verification Script: Schema Agent & Dynamic MySQL Inspection.
Tests:
1. SchemaLoader live introspection of 11 MySQL tables
2. DDL-like schema serialization
3. SchemaAgent dynamic table selection across 4 different query scenarios
"""

import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.database.schema_loader import SchemaLoader, DatabaseSchema
from app.agents.schema_agent import SchemaAgent, SchemaAgentResult

print("==================================================")
print("  PHASE 4 VERIFICATION: SCHEMA AGENT & INSPECTION ")
print("==================================================")

print("\n--> 1. Testing Dynamic SchemaLoader from MySQL...")
schema: DatabaseSchema = SchemaLoader.load_schema(force_reload=True)
print(f"    Database Name: {schema.database_name}")
print(f"    Loaded Tables Count: {len(schema.tables)}")
for tbl_name, tbl in schema.tables.items():
    print(f"      - `{tbl.name}` ({tbl.row_count:,} rows, {len(tbl.columns)} cols, PK: {tbl.primary_keys}, FKs: {len(tbl.foreign_keys)})")

assert len(schema.tables) == 11, f"Expected 11 tables, got {len(schema.tables)}"
assert "sales" in schema.tables
assert "orders" in schema.tables
assert "products" in schema.tables
print("    [PASS] Dynamic Schema Introspection Verified.")

print("\n--> 2. Testing DDL Serialization Format...")
serialized_full = SchemaLoader.serialize_schema(schema, included_tables={"sales", "regions"})
print(f"    Sample Serialized Output (sales + regions):\n")
for line in serialized_full.split("\n")[:15]:
    print(f"      {line}")
print("      ...")
assert "TABLE `sales`" in serialized_full or "TABLE `regions`" in serialized_full
print("    [PASS] Serialization Format Verified.")

print("\n--> 3. Testing SchemaAgent Dynamic Table & Column Selection...")

test_queries = [
    (
        "Sales by Region Query",
        "Show total revenue and profit by region for 2024.",
        {"sales", "regions"}
    ),
    (
        "Employee Performance Query",
        "Which sales employee generated the most revenue in 2023?",
        {"employees"}
    ),
    (
        "Inventory Stock Query",
        "Which warehouse has low stock for Electronics products?",
        {"inventory", "products"}
    ),
    (
        "Payment Methods Query",
        "What are the top payment methods by transaction volume in Chennai?",
        {"payments"}
    ),
]

for test_name, query, expected_must_include in test_queries:
    print(f"\n    Testing: {test_name}")
    print(f"    Query: \"{query}\"")
    result: SchemaAgentResult = SchemaAgent.select_schema_context(user_query=query, schema=schema)
    print(f"    Selected Tables: {result.relevant_tables}")
    print(f"    Suggested Joins: {result.suggested_joins}")
    print(f"    Reasoning: {result.reasoning}")

    selected_set = {t.lower() for t in result.relevant_tables}
    for expected_tbl in expected_must_include:
        assert any(expected_tbl in t for t in selected_set), f"Query '{query}' expected to include table '{expected_tbl}', got: {selected_set}"
    assert len(result.serialized_schema) > 50, "Serialized schema should not be empty"

print("\n=== PHASE 4 VERIFICATION COMPLETE: ALL CHECKS PASSED ===")
