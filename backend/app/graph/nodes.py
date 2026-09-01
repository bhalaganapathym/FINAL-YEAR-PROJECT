"""
LangGraph Multi-Agent Workflow Nodes.
Implements each isolated agent node with dynamic multi-database routing:
- Intent Node
- Schema Node
- SQL Generation Node
- SQL Validation Node
- SQL Execution Node
- Result Analysis Node
- Insight Node
- Visualization Node
- Forecast Node
- Response Synthesis Node
"""

from typing import Any, Dict
from app.graph.state import AgentState
from app.agents.intent_agent import IntentAgent
from app.agents.schema_agent import SchemaAgent
from app.agents.sql_agent import SQLGenerationAgent
from app.agents.validation_agent import SQLValidationAgent
from app.database.executor import SQLExecutor
from app.database.schema_loader import SchemaLoader
from app.agents.analysis_agent import ResultAnalysisAgent
from app.agents.insight_agent import InsightAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.forecast_agent import ForecastAgent
from app.utils.logger import logger


def intent_node(state: AgentState) -> Dict[str, Any]:
    """
    Classify analytical intent and resolve multi-turn conversational context.
    """
    logger.info(f"[GRAPH NODE: Intent] Processing: '{state['user_query']}'")
    intent_output = IntentAgent.classify_intent(
        user_query=state["user_query"],
        conversation_history=state.get("conversation_history", [])
    )

    return {
        "intent": intent_output.model_dump(),
        "resolved_query": intent_output.resolved_query,
        "visualization_required": intent_output.visualization_required,
        "forecast_required": intent_output.forecast_required,
    }


def schema_node(state: AgentState) -> Dict[str, Any]:
    """
    Dynamically introspect and select minimal relevant schema context from target database.
    """
    query = state.get("resolved_query") or state["user_query"]
    db_id = state.get("database_id")
    logger.info(f"[GRAPH NODE: Schema] Selecting tables for '{query}' on database '{db_id or 'default'}'")

    db_schema = SchemaLoader.load_schema(database_id=db_id)
    schema_result = SchemaAgent.select_schema_context(user_query=query, schema=db_schema)

    return {
        "relevant_tables": schema_result.relevant_tables,
        "relevant_columns": schema_result.relevant_columns,
        "suggested_joins": schema_result.suggested_joins,
        "serialized_schema": schema_result.serialized_schema,
    }


def sql_generation_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate or self-correct SQL query grounded in schema and error feedback.
    """
    query = state.get("resolved_query") or state["user_query"]
    retries = state.get("retry_count", 0)

    error_feedback = None
    if state.get("validation_errors"):
        error_feedback = f"Validation Errors: {'; '.join(state['validation_errors'])}"
    elif state.get("execution_error"):
        error_feedback = f"Database Execution Error: {state['execution_error']}"

    logger.info(f"[GRAPH NODE: SQL Generation] Attempt {retries + 1} for: '{query}'" + (f" [Fixing: {error_feedback[:60]}...]" if error_feedback else ""))

    sql_output = SQLGenerationAgent.generate_sql(
        user_query=query,
        serialized_schema=state.get("serialized_schema", ""),
        intent_info=state.get("intent"),
        error_feedback=error_feedback,
        previous_sql=state.get("generated_sql"),
    )

    return {
        "generated_sql": sql_output.sql,
        "sql_reasoning": sql_output.reasoning,
        "retry_count": retries + 1 if error_feedback else 0,
        "validation_errors": [],
        "execution_error": None,
    }


def sql_validation_node(state: AgentState) -> Dict[str, Any]:
    """
    Validate SQL for AST syntax, non-existent tables/columns, and DML safety.
    """
    sql = state.get("generated_sql", "")
    db_id = state.get("database_id")
    logger.info(f"[GRAPH NODE: Validation] Inspecting SQL: {sql[:80]}...")

    db_schema = SchemaLoader.load_schema(database_id=db_id)
    validation = SQLValidationAgent.validate_sql(
        sql=sql,
        user_query=state.get("resolved_query"),
        schema=db_schema,
    )

    return {
        "is_valid_sql": validation.is_valid,
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
    }


def sql_execution_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute validated SQL query safely against target MySQL or session uploaded database.
    """
    sql = state.get("generated_sql", "")
    db_id = state.get("database_id")
    logger.info(f"[GRAPH NODE: Execution] Executing SQL on db '{db_id or 'default'}': {sql[:80]}...")

    res = SQLExecutor.execute(sql, database_id=db_id)

    return {
        "execution_success": res.success,
        "execution_result": res.model_dump(),
        "execution_error": res.error_message,
        "query_data": res.data,
        "query_columns": res.columns,
        "execution_time_ms": res.execution_time_ms,
    }


def result_analysis_node(state: AgentState) -> Dict[str, Any]:
    """
    Perform statistical pattern extraction and natural business explanation.
    """
    data = state.get("query_data", [])
    columns = state.get("query_columns", [])
    query = state.get("resolved_query") or state["user_query"]
    sql = state.get("generated_sql", "")

    logger.info(f"[GRAPH NODE: Analysis] Analyzing {len(data)} result rows...")

    analysis = ResultAnalysisAgent.analyze(
        user_query=query,
        sql_query=sql,
        data=data,
        columns=columns,
    )

    return {
        "analysis_summary": analysis.summary,
        "key_findings": analysis.key_findings,
    }


def insight_node(state: AgentState) -> Dict[str, Any]:
    """
    Extract 3-5 executive-level business insight bullets.
    """
    data = state.get("query_data", [])
    columns = state.get("query_columns", [])
    query = state.get("resolved_query") or state["user_query"]
    summary = state.get("analysis_summary", "")

    logger.info("[GRAPH NODE: Insights] Formulating business insights...")

    insights_list = InsightAgent.generate_insights(
        user_query=query,
        analysis_summary=summary,
        data=data,
        columns=columns,
    )

    return {
        "insights": insights_list,
    }


def visualization_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate Plotly interactive chart payload.
    """
    data = state.get("query_data", [])
    columns = state.get("query_columns", [])
    query = state.get("resolved_query") or state["user_query"]

    logger.info("[GRAPH NODE: Visualization] Checking visualization feasibility...")

    viz_payload = VisualizationAgent.generate_visualization(
        data=data,
        columns=columns,
        user_query=query,
    )

    return {
        "visualization_data": viz_payload,
    }


def forecast_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate statistical time-series forecast using statsforecast.
    """
    data = state.get("query_data", [])
    columns = state.get("query_columns", [])
    query = state.get("resolved_query") or state["user_query"]

    logger.info("[GRAPH NODE: Forecast] Generating time-series forecast...")

    forecast_payload = ForecastAgent.run_forecast(
        data=data,
        columns=columns,
        horizon=6,
        user_query=query,
    )

    return {
        "forecast_result": forecast_payload,
    }


def response_synthesis_node(state: AgentState) -> Dict[str, Any]:
    """
    Synthesize the final natural language answer for the user.
    """
    summary = state.get("analysis_summary") or "Query executed successfully."
    error = state.get("execution_error") or ("; ".join(state.get("validation_errors", [])) if not state.get("is_valid_sql") else None)

    if error:
        final_ans = f"I encountered an issue processing your request: {error}"
    else:
        final_ans = summary

    logger.info(f"[GRAPH NODE: Synthesizer] Final answer compiled.")

    return {
        "final_answer": final_ans,
        "error_message": error,
    }
