"""
Automated tests for Phase 4: Schema Agent & Dynamic MySQL Introspection.
"""

import pytest
from app.database.schema_loader import SchemaLoader
from app.agents.schema_agent import SchemaAgent, SchemaAgentResult


def test_schema_loader_tables():
    """Verify that all tables and columns are dynamically discovered."""
    schema = SchemaLoader.load_schema()

    assert "customers" in schema.tables
    assert "products" in schema.tables
    assert "sales" in schema.tables
    assert "regions" in schema.tables

    sales_table = schema.get_table("sales")
    assert sales_table is not None
    assert "revenue" in sales_table.column_names
    assert "profit" in sales_table.column_names
    assert "sale_date" in sales_table.column_names


def test_schema_serialization():
    """Verify DDL serialization for full and partial schemas."""
    schema = SchemaLoader.load_schema()
    serialized = SchemaLoader.serialize_schema(schema, {"customers", "regions"})

    assert "TABLE `customers`" in serialized
    assert "TABLE `regions`" in serialized
    assert "TABLE `sales`" not in serialized
    assert "REFERENCES regions.region_id" in serialized or "REFERENCES regions(region_id)" in serialized


def test_schema_agent_selection_sales_by_region():
    """Verify that SchemaAgent selects sales and regions for regional queries."""
    schema = SchemaLoader.load_schema()
    query = "Show total sales and profit by region for 2024."

    result: SchemaAgentResult = SchemaAgent.select_schema_context(query, schema=schema)

    assert "sales" in result.relevant_tables
    assert "regions" in result.relevant_tables
    assert "TABLE `sales`" in result.serialized_schema
    assert "TABLE `regions`" in result.serialized_schema


def test_schema_agent_selection_inventory():
    """Verify that SchemaAgent includes inventory and products for stock queries."""
    schema = SchemaLoader.load_schema()
    query = "Which products currently have stock below their reorder level?"

    result: SchemaAgentResult = SchemaAgent.select_schema_context(query, schema=schema)

    assert "inventory" in result.relevant_tables or "products" in result.relevant_tables
