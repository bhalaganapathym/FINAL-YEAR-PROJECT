"""
LangGraph Multi-Agent Stateful Workflow Orchestrator.
Assembles the complete state machine with conditional routing, self-correction loops,
and SQLite checkpoint persistence.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.config import get_settings
from app.graph.state import AgentState
from app.graph.nodes import (
    intent_node,
    schema_node,
    sql_generation_node,
    sql_validation_node,
    sql_execution_node,
    result_analysis_node,
    insight_node,
    visualization_node,
    forecast_node,
    response_synthesis_node,
)
from app.memory.checkpoint import get_sqlite_checkpointer
from app.utils.logger import logger

settings = get_settings()


def should_retry_after_validation(state: AgentState) -> Literal["sql_generation_node", "sql_execution_node", "response_synthesis_node"]:
    """
    Conditional routing edge after SQL validation.
    """
    is_valid = state.get("is_valid_sql", False)
    retries = state.get("retry_count", 0)

    if is_valid:
        return "sql_execution_node"

    if retries < settings.MAX_RETRY_COUNT:
        logger.warning(f"SQL validation failed. Triggering Self-Correction attempt ({retries + 1}/{settings.MAX_RETRY_COUNT})...")
        return "sql_generation_node"

    logger.error("Maximum validation retry limit exceeded. Routing to response synthesis.")
    return "response_synthesis_node"


def should_retry_after_execution(state: AgentState) -> Literal["sql_generation_node", "result_analysis_node", "response_synthesis_node"]:
    """
    Conditional routing edge after SQL execution.
    """
    success = state.get("execution_success", False)
    retries = state.get("retry_count", 0)

    if success:
        return "result_analysis_node"

    if retries < settings.MAX_RETRY_COUNT:
        logger.warning(f"SQL database execution failed. Triggering Self-Correction attempt ({retries + 1}/{settings.MAX_RETRY_COUNT})...")
        return "sql_generation_node"

    logger.error("Maximum execution retry limit exceeded. Routing to response synthesis.")
    return "response_synthesis_node"


def route_after_insights(state: AgentState) -> Literal["visualization_node", "forecast_node", "response_synthesis_node"]:
    """
    Conditional routing for visual and predictive enrichments.
    """
    if state.get("visualization_required", False):
        return "visualization_node"
    if state.get("forecast_required", False):
        return "forecast_node"
    return "response_synthesis_node"


def route_after_visualization(state: AgentState) -> Literal["forecast_node", "response_synthesis_node"]:
    """
    Routing from visualization node to forecast or synthesis.
    """
    if state.get("forecast_required", False):
        return "forecast_node"
    return "response_synthesis_node"


def build_analytics_graph(with_checkpointer: bool = True):
    """
    Construct, wire, and compile the LangGraph state machine.
    """
    workflow = StateGraph(AgentState)

    # 1. Register All Agent Nodes
    workflow.add_node("intent_node", intent_node)
    workflow.add_node("schema_node", schema_node)
    workflow.add_node("sql_generation_node", sql_generation_node)
    workflow.add_node("sql_validation_node", sql_validation_node)
    workflow.add_node("sql_execution_node", sql_execution_node)
    workflow.add_node("result_analysis_node", result_analysis_node)
    workflow.add_node("insight_node", insight_node)
    workflow.add_node("visualization_node", visualization_node)
    workflow.add_node("forecast_node", forecast_node)
    workflow.add_node("response_synthesis_node", response_synthesis_node)

    # 2. Wire Direct and Conditional Edges
    workflow.add_edge(START, "intent_node")
    workflow.add_edge("intent_node", "schema_node")
    workflow.add_edge("schema_node", "sql_generation_node")
    workflow.add_edge("sql_generation_node", "sql_validation_node")

    # Validation self-correction loop
    workflow.add_conditional_edges(
        "sql_validation_node",
        should_retry_after_validation,
        {
            "sql_generation_node": "sql_generation_node",
            "sql_execution_node": "sql_execution_node",
            "response_synthesis_node": "response_synthesis_node",
        }
    )

    # Execution self-correction loop
    workflow.add_conditional_edges(
        "sql_execution_node",
        should_retry_after_execution,
        {
            "sql_generation_node": "sql_generation_node",
            "result_analysis_node": "result_analysis_node",
            "response_synthesis_node": "response_synthesis_node",
        }
    )

    workflow.add_edge("result_analysis_node", "insight_node")

    # Post-insight branching to visualization and forecast
    workflow.add_conditional_edges(
        "insight_node",
        route_after_insights,
        {
            "visualization_node": "visualization_node",
            "forecast_node": "forecast_node",
            "response_synthesis_node": "response_synthesis_node",
        }
    )

    workflow.add_conditional_edges(
        "visualization_node",
        route_after_visualization,
        {
            "forecast_node": "forecast_node",
            "response_synthesis_node": "response_synthesis_node",
        }
    )

    workflow.add_edge("forecast_node", "response_synthesis_node")
    workflow.add_edge("response_synthesis_node", END)

    # 3. Compile Graph with SQLite Persistence Checkpointer
    checkpointer = get_sqlite_checkpointer() if with_checkpointer else None
    app_graph = workflow.compile(checkpointer=checkpointer)

    return app_graph


# Pre-compiled workflow graph instance
analytics_graph = build_analytics_graph()
