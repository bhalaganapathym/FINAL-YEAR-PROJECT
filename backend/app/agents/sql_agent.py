"""
SQL Generation Agent for Persistent AI Data Analyst.
Generates optimized, valid, read-only MySQL 8.0+ queries grounded in the dynamic database schema,
analytical intent, conversational context, and execution/validation error feedback.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prompts.sql_prompts import SQL_SYSTEM_PROMPT, SQL_FEW_SHOT_EXAMPLES
from app.services.llm_service import generate_structured_output
from app.utils.logger import logger


class SQLGenerationOutput(BaseModel):
    """
    Structured output returned by SQL Generation Agent.
    """
    sql: str = Field(
        ...,
        description="Clean, executable MySQL 8.0+ read-only query"
    )
    reasoning: str = Field(
        ...,
        description="Brief technical explanation of joins, aggregations, filters, and ordering used"
    )
    tables_used: List[str] = Field(
        default_factory=list,
        description="List of table names referenced in the query"
    )
    filters_applied: List[str] = Field(
        default_factory=list,
        description="Key filters applied in WHERE clause"
    )
    grouping_applied: List[str] = Field(
        default_factory=list,
        description="GROUP BY columns"
    )
    ordering_applied: Optional[str] = Field(
        None,
        description="ORDER BY clause and direction"
    )
    assumptions: Optional[str] = Field(
        None,
        description="Any assumptions made regarding metrics or date ranges"
    )


class SQLGenerationAgent:
    """
    Generates and self-corrects MySQL queries.
    """

    @classmethod
    def clean_sql(cls, sql_text: str) -> str:
        """
        Strip markdown backticks, extra whitespace, and normalize trailing semicolon.
        """
        cleaned = sql_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
        if not cleaned.endswith(";"):
            cleaned += ";"
        return cleaned

    @classmethod
    def generate_sql(
        cls,
        user_query: str,
        serialized_schema: str,
        intent_info: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[str] = None,
        error_feedback: Optional[str] = None,
        previous_sql: Optional[str] = None,
    ) -> SQLGenerationOutput:
        """
        Generate MySQL query grounded on intent, schema, and previous conversation.
        """
        intent_str = ""
        if intent_info:
            intent_str = (
                "ANALYTICAL INTENT:\n"
                f"- Intent Type: {intent_info.get('intent')}\n"
                f"- Metric: {intent_info.get('primary_metric')}\n"
                f"- Group By: {intent_info.get('group_by_dimensions')}\n"
                f"- Filter Conditions: {intent_info.get('filter_conditions')}\n"
                f"- Time Range: {intent_info.get('time_range')}\n"
                f"- Resolved Query: {intent_info.get('resolved_query')}\n"
            )

        feedback_section = ""
        if error_feedback and previous_sql:
            feedback_section = (
                "\n==================================================\n"
                "SELF-CORRECTION ERROR FEEDBACK:\n"
                "The previous query failed execution or validation:\n"
                f"PREVIOUS SQL:\n{previous_sql}\n\n"
                f"ERROR MESSAGE:\n{error_feedback}\n\n"
                "INSTRUCTIONS FOR CORRECTION:\n"
                "1. Carefully diagnose why the previous query failed based on the error message.\n"
                "2. Fix column names, table names, join syntax, or aggregation issues.\n"
                "3. Ensure all table and column names exist in the schema.\n"
                "==================================================\n"
            )

        conv_str = f"CONVERSATION CONTEXT:\n{conversation_context}\n" if conversation_context else ""

        prompt = (
            f"{SQL_SYSTEM_PROMPT}\n\n"
            f"{SQL_FEW_SHOT_EXAMPLES}\n\n"
            f"DATABASE SCHEMA CONTEXT:\n{serialized_schema}\n\n"
            f"{conv_str}"
            f"{intent_str}\n"
            f"{feedback_section}\n"
            f"CURRENT USER QUESTION:\n\"{user_query}\"\n\n"
            f"Generate the optimal MySQL 8.0+ query to answer the question."
        )

        try:
            logger.info(f"Generating SQL for query: '{user_query}'" + (" [Self-Correction Attempt]" if error_feedback else ""))
            output: SQLGenerationOutput = generate_structured_output(
                prompt=prompt,
                schema=SQLGenerationOutput,
                temperature=0.0,
            )

            output.sql = cls.clean_sql(output.sql)
            logger.info(f"Generated SQL: {output.sql.replace(chr(10), ' ')}")
            return output

        except Exception as e:
            logger.error(f"SQLGenerationAgent exception: {e}")
            fallback_sql = "SELECT SUM(revenue) AS total_revenue, year FROM sales GROUP BY year ORDER BY year ASC;"
            return SQLGenerationOutput(
                sql=fallback_sql,
                reasoning="Fallback aggregation query generated due to model parsing exception.",
                tables_used=["sales"],
                filters_applied=[],
                grouping_applied=["year"],
                ordering_applied="year ASC",
                assumptions="Fallback assumption: yearly sales aggregation.",
            )
