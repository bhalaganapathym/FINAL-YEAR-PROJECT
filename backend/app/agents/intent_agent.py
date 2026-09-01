"""
Intent Classification Agent for Persistent AI Data Analyst.
Extracts analytical intent, metrics, grouping dimensions, filters, time horizons,
and execution flags (visualization, forecasting) while resolving multi-turn conversational follow-ups.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prompts.intent_prompts import INTENT_SYSTEM_PROMPT
from app.services.llm_service import generate_structured_output
from app.utils.logger import logger


class IntentOutput(BaseModel):
    """
    Structured analytical intent extracted from user query.
    """
    intent: str = Field(
        ...,
        description="Analytical intent category: aggregation, ranking, comparison, trend, filter, forecasting, general_query"
    )
    primary_metric: str = Field(
        ...,
        description="Core metric requested: revenue, profit, quantity, order_count, discount, stock_quantity, salary, etc."
    )
    group_by_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions to group by (e.g., ['region', 'month', 'category', 'product_name', 'city'])"
    )
    filter_conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted filter conditions (e.g., {'city': 'Chennai', 'year': 2024, 'status': 'Completed'})"
    )
    time_range: Optional[str] = Field(
        None,
        description="Time range specified in query (e.g., '2024', 'Q3 2023', 'last 6 months')"
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Key named business entities mentioned (e.g., ['Chennai', 'Electronics', 'Suresh Iyer'])"
    )
    visualization_required: bool = Field(
        default=False,
        description="True if query results should be visualized as a chart or graph"
    )
    forecast_required: bool = Field(
        default=False,
        description="True if user specifically requests future prediction/forecast"
    )
    comparison_required: bool = Field(
        default=False,
        description="True if comparing two or more entities, regions, or timeframes"
    )
    resolved_query: str = Field(
        ...,
        description="Standalone formulation of the user query with pronouns and conversational context fully resolved"
    )
    reasoning: str = Field(
        ...,
        description="Brief reasoning behind intent classification and context resolution"
    )


class IntentAgent:
    """
    Understands user intent and resolves conversational follow-ups.
    """

    @classmethod
    def classify_intent(
        cls,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> IntentOutput:
        """
        Classify analytical intent and resolve conversational context.
        """
        if conversation_history:
            history_lines = []
            for item in conversation_history[-4:]:
                role = item.get("role", "user")
                content = item.get("content", "")
                sql = item.get("sql", "")
                sql_info = f" [Executed SQL: {sql}]" if sql else ""
                history_lines.append(f"{role.capitalize()}: {content}{sql_info}")
            history_header = "CONVERSATION HISTORY:\n" + "\n".join(history_lines) + "\n"
        else:
            history_header = "CONVERSATION HISTORY: None (This is the start of the session).\n"

        prompt = (
            f"{INTENT_SYSTEM_PROMPT}\n\n"
            f"{history_header}\n"
            f"CURRENT USER QUERY:\n\"{user_query}\"\n\n"
            f"Extract the structured intent and provide a clean resolved_query."
        )

        try:
            logger.info(f"Classifying intent for query: '{user_query}'")
            result: IntentOutput = generate_structured_output(
                prompt=prompt,
                schema=IntentOutput,
                temperature=0.0,
            )
            logger.info(f"Intent classified: {result.intent} | metric: {result.primary_metric} | viz: {result.visualization_required} | forecast: {result.forecast_required}")
            return result

        except Exception as e:
            logger.error(f"IntentAgent error: {e}. Falling back to default intent.")
            return IntentOutput(
                intent="general_query",
                primary_metric="revenue",
                group_by_dimensions=[],
                filter_conditions={},
                time_range=None,
                entities=[],
                visualization_required=True,
                forecast_required="forecast" in user_query.lower() or "predict" in user_query.lower(),
                comparison_required="compare" in user_query.lower(),
                resolved_query=user_query,
                reasoning="Fallback intent due to extraction exception.",
            )
