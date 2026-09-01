"""
API route definitions for Persistent AI Data Analyst.
Exposes /health, /query, and /conversation endpoints.
"""

import uuid
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import (
    HealthResponse,
    DatabaseHealth,
    QueryRequest,
    QueryResponse,
    ConversationHistoryResponse,
)
from app.database.connection import test_db_connection
from app.services.query_service import QueryService, active_sessions
from app.utils.logger import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Service and database health check endpoint.
    """
    logger.info("Health check endpoint invoked")
    db_ok, db_msg, db_latency = test_db_connection()

    db_health = DatabaseHealth(
        connected=db_ok,
        database_name="business_analytics" if db_ok else None,
        latency_ms=round(db_latency, 2),
        error=None if db_ok else db_msg,
    )

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version="1.0.0",
        database=db_health,
    )


@router.post("/query", response_model=QueryResponse, tags=["Analytics"])
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process natural language analytics question through the LangGraph Multi-Agent pipeline.
    """
    logger.info(f"Incoming query: '{request.query}' | conversation_id: {request.conversation_id}")
    response = await QueryService.process_user_query(request)
    return response


@router.get("/conversation/{conversation_id}", response_model=ConversationHistoryResponse, tags=["Memory"])
async def get_conversation_history(conversation_id: str) -> ConversationHistoryResponse:
    """
    Fetch interaction history for a given conversation session.
    """
    logger.info(f"Retrieving conversation history for: {conversation_id}")
    session = active_sessions.get(conversation_id)
    if not session:
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=[]
        )

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[t.model_dump() for t in session.turns]
    )
