"""
Schema Agent for Persistent AI Data Analyst.
Analyzes user query and intent, selects relevant tables/columns from the dynamic MySQL schema,
and serializes a compact schema context with join recommendations for the SQL Generation Agent.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from app.database.schema_loader import SchemaLoader, DatabaseSchema
from app.services.llm_service import generate_structured_output
from app.utils.logger import logger


class SchemaSelectionOutput(BaseModel):
    """
    LLM structured output for table and column relevance.
    """
    relevant_tables: List[str] = Field(
        ...,
        description="Names of database tables required to answer the query (e.g., ['sales', 'regions', 'products'])"
    )
    relevant_columns: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Dictionary mapping table name to relevant column names"
    )
    suggested_joins: List[str] = Field(
        default_factory=list,
        description="Suggested join conditions between the tables (e.g., ['orders.customer_id = customers.customer_id'])"
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation of why these schema elements were chosen"
    )


class SchemaAgentResult(BaseModel):
    """
    Complete output package produced by SchemaAgent.
    """
    relevant_tables: List[str]
    relevant_columns: Dict[str, List[str]]
    suggested_joins: List[str]
    serialized_schema: str
    reasoning: str


class SchemaAgent:
    """
    Intelligent Schema Selector and Context Provider.
    """

    @classmethod
    def get_full_schema_summary(cls, schema: DatabaseSchema) -> str:
        """
        Generate a concise catalog of table names, row counts, and column lists.
        """
        catalog = []
        for name, table in schema.tables.items():
            cols = ", ".join(table.column_names)
            catalog.append(f"- `{table.name}` ({table.row_count or 0} rows): [{cols}]")
        return "\n".join(catalog)

    @classmethod
    def select_schema_context(
        cls,
        user_query: str,
        conversation_context: Optional[str] = None,
        schema: Optional[DatabaseSchema] = None,
    ) -> SchemaAgentResult:
        """
        Identify relevant tables/columns for user_query and serialize targeted schema.
        """
        db_schema = schema or SchemaLoader.load_schema()
        table_catalog = cls.get_full_summary(db_schema)
        conv_text = f"CONVERSATION CONTEXT: {conversation_context}\n" if conversation_context else ""

        prompt = (
            "You are the Schema Agent in a multi-agent text-to-SQL system.\n"
            "Your task is to analyze the user's question and determine the minimal set of relevant tables, columns, and join paths from the database.\n\n"
            f"DATABASE: {db_schema.database_name}\n\n"
            f"AVAILABLE TABLES & COLUMNS:\n{table_catalog}\n\n"
            f"{conv_text}"
            f"USER QUESTION:\n\"{user_query}\"\n\n"
            "INSTRUCTIONS:\n"
            "1. Select only tables and columns needed to accurately answer the question.\n"
            "2. Note: For fast sales/revenue/profit reporting, the `sales` table contains pre-aggregated dimensions (year, month, quarter, revenue, profit, quantity, product_id, customer_id, region_id).\n"
            "3. If granular order item or customer details are needed, include `orders`, `order_items`, `customers`, `products`, `employees`, etc.\n"
            "4. Ensure all chosen table names strictly match the available tables list.\n"
            "5. Provide explicit join conditions between the chosen tables."
        )

        try:
            selection: SchemaSelectionOutput = generate_structured_output(
                prompt=prompt,
                schema=SchemaSelectionOutput,
                temperature=0.0,
            )

            # Validate that selected tables exist in schema
            valid_tables: Set[str] = set()
            for tbl in selection.relevant_tables:
                clean_tbl = tbl.strip().lower()
                if clean_tbl in db_schema.tables:
                    valid_tables.add(clean_tbl)

            # Fallback if no valid tables found
            if not valid_tables:
                logger.warning("No valid tables identified by LLM; defaulting to core analytical tables.")
                valid_tables = {"sales", "regions", "products", "customers"}

            serialized = SchemaLoader.serialize_schema(
                schema=db_schema,
                included_tables=valid_tables,
            )

            logger.info(f"SchemaAgent selected {len(valid_tables)} tables: {list(valid_tables)}")

            return SchemaAgentResult(
                relevant_tables=list(valid_tables),
                relevant_columns=selection.relevant_columns,
                suggested_joins=selection.suggested_joins,
                serialized_schema=serialized,
                reasoning=selection.reasoning,
            )

        except Exception as e:
            logger.error(f"SchemaAgent selection error: {e}. Falling back to default schema.")
            core_tables = {"sales", "regions", "products", "customers", "orders"}
            serialized = SchemaLoader.serialize_schema(db_schema, core_tables)
            return SchemaAgentResult(
                relevant_tables=list(core_tables),
                relevant_columns={},
                suggested_joins=[],
                serialized_schema=serialized,
                reasoning="Fallback to default analytical tables due to selection exception.",
            )

    @classmethod
    def get_full_summary(cls, schema: DatabaseSchema) -> str:
        return cls.get_full_schema_summary(schema)
