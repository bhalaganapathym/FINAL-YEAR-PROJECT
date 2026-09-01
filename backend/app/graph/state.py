"""
Strongly Typed LangGraph State Definition.
Uses TypedDict with Annotated fields for reducer operations.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated, TypedDict


def replace_reducer(current: Any, new_val: Any) -> Any:
    """Default state field update reducer."""
    return new_val


def append_list_reducer(current: List[Any], new_items: List[Any]) -> List[Any]:
    """Append list reducer for error histories and warnings."""
    if current is None:
        current = []
    if new_items is None:
        return current
    return current + new_items


class AgentState(TypedDict):
    """
    Multi-Agent LangGraph State.
    Maintains all intermediate representations across nodes, databases, and multi-turn loops.
    """
    # User Input & Session Identification
    user_query: Annotated[str, replace_reducer]
    conversation_id: Annotated[str, replace_reducer]
    database_id: Annotated[Optional[str], replace_reducer]
    conversation_history: Annotated[List[Dict[str, Any]], replace_reducer]

    # Intent Classification
    intent: Annotated[Optional[Dict[str, Any]], replace_reducer]
    resolved_query: Annotated[Optional[str], replace_reducer]

    # Schema Grounding
    relevant_tables: Annotated[List[str], replace_reducer]
    relevant_columns: Annotated[Dict[str, List[str]], replace_reducer]
    suggested_joins: Annotated[List[str], replace_reducer]
    serialized_schema: Annotated[Optional[str], replace_reducer]

    # SQL Generation & Validation
    generated_sql: Annotated[Optional[str], replace_reducer]
    sql_reasoning: Annotated[Optional[str], replace_reducer]
    is_valid_sql: Annotated[bool, replace_reducer]
    validation_errors: Annotated[List[str], append_list_reducer]
    validation_warnings: Annotated[List[str], append_list_reducer]
    retry_count: Annotated[int, replace_reducer]

    # Execution Engine
    execution_success: Annotated[bool, replace_reducer]
    execution_result: Annotated[Optional[Dict[str, Any]], replace_reducer]
    execution_error: Annotated[Optional[str], replace_reducer]
    query_data: Annotated[List[Dict[str, Any]], replace_reducer]
    query_columns: Annotated[List[str], replace_reducer]
    execution_time_ms: Annotated[float, replace_reducer]

    # Analytical Explanations & Insights
    analysis_summary: Annotated[Optional[str], replace_reducer]
    key_findings: Annotated[List[str], replace_reducer]
    insights: Annotated[List[str], replace_reducer]

    # Visualizations & Forecasts
    visualization_required: Annotated[bool, replace_reducer]
    visualization_data: Annotated[Optional[Dict[str, Any]], replace_reducer]
    forecast_required: Annotated[bool, replace_reducer]
    forecast_result: Annotated[Optional[Dict[str, Any]], replace_reducer]

    # Final Synthesized Response
    final_answer: Annotated[Optional[str], replace_reducer]
    error_message: Annotated[Optional[str], replace_reducer]
