"""
Query Service for Persistent AI Data Analyst.
Coordinates request lifecycle, invokes the LangGraph stateful multi-agent graph,
manages conversation thread IDs, and returns structured API responses.
"""

import time
import uuid
from typing import Any, Dict, List, Optional
from app.api.schemas import QueryRequest, QueryResponse, VisualizationPayload, ForecastPayload
from app.graph.workflow import analytics_graph
from app.memory.conversation import ConversationSession
from app.utils.logger import logger

# In-memory session tracking for quick conversation lookups
active_sessions: Dict[str, ConversationSession] = {}


class QueryService:
    """
    Orchestrates end-to-end question processing through LangGraph.
    """

    @classmethod
    def get_or_create_session(cls, conversation_id: str) -> ConversationSession:
        if conversation_id not in active_sessions:
            active_sessions[conversation_id] = ConversationSession(conversation_id=conversation_id)
        return active_sessions[conversation_id]

    @classmethod
    async def process_user_query(cls, request: QueryRequest) -> QueryResponse:
        """
        Execute full multi-agent pipeline for user query.
        """
        start_time = time.time()
        conv_id = request.conversation_id or str(uuid.uuid4())
        session = cls.get_or_create_session(conv_id)

        # Record incoming user turn
        session.add_user_turn(request.query)

        # Prepare initial LangGraph state with target database_id
        initial_state = {
            "user_query": request.query,
            "conversation_id": conv_id,
            "database_id": request.database_id,
            "conversation_history": [t.model_dump() for t in session.turns[:-1]],
            "intent": None,
            "resolved_query": None,
            "relevant_tables": [],
            "relevant_columns": {},
            "suggested_joins": [],
            "serialized_schema": None,
            "generated_sql": None,
            "sql_reasoning": None,
            "is_valid_sql": False,
            "validation_errors": [],
            "validation_warnings": [],
            "retry_count": 0,
            "execution_success": False,
            "execution_result": None,
            "execution_error": None,
            "query_data": [],
            "query_columns": [],
            "execution_time_ms": 0.0,
            "analysis_summary": None,
            "key_findings": [],
            "insights": [],
            "visualization_required": False,
            "visualization_data": None,
            "forecast_required": False,
            "forecast_result": None,
            "final_answer": None,
            "error_message": None,
        }

        # LangGraph Thread Config for SQLite checkpointing
        config = {"configurable": {"thread_id": conv_id}}

        logger.info(f"Invoking LangGraph Multi-Agent Orchestrator [Thread: {conv_id}, DB: {request.database_id or 'default'}]...")

        try:
            final_state = analytics_graph.invoke(initial_state, config=config)

            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            # Extract final payload components
            answer = final_state.get("final_answer") or "Analysis completed."
            sql = final_state.get("generated_sql")
            data = final_state.get("query_data", [])
            columns = final_state.get("query_columns", [])
            insights = final_state.get("insights", [])

            # Visualization payload
            viz_dict = final_state.get("visualization_data")
            viz_payload = None
            if viz_dict:
                viz_payload = VisualizationPayload(
                    type=viz_dict.get("type", "bar"),
                    figure=viz_dict.get("figure", {}),
                    title=viz_dict.get("title"),
                )

            # Forecast payload
            fc_dict = final_state.get("forecast_result")
            fc_payload = None
            if fc_dict:
                fc_payload = ForecastPayload(
                    metric=fc_dict.get("metric", "value"),
                    time_column=fc_dict.get("time_column", "date"),
                    horizon=fc_dict.get("horizon", 6),
                    predictions=fc_dict.get("predictions", []),
                    confidence_intervals=fc_dict.get("confidence_intervals"),
                    figure=fc_dict.get("figure"),
                )

            # Save assistant response to session
            session.add_assistant_turn(
                answer=answer,
                sql=sql,
                data_summary=f"{len(data)} rows returned"
            )

            return QueryResponse(
                conversation_id=conv_id,
                question=request.query,
                answer=answer,
                sql=sql,
                data=data,
                columns=columns,
                insights=insights,
                visualization=viz_payload,
                forecast=fc_payload,
                execution_time_ms=elapsed_ms,
                error=final_state.get("error_message"),
            )

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"LangGraph execution exception: {e}")
            return QueryResponse(
                conversation_id=conv_id,
                question=request.query,
                answer=f"Sorry, I encountered an unexpected error while analyzing your question: {str(e)}",
                sql=None,
                data=[],
                columns=[],
                insights=[],
                visualization=None,
                forecast=None,
                execution_time_ms=elapsed_ms,
                error=str(e),
            )
