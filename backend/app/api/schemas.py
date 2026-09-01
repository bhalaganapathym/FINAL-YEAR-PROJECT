"""
Pydantic API request and response data contracts.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    """
    Database connection status information.
    """
    connected: bool = Field(..., description="True if database connection is active")
    database_name: Optional[str] = Field(None, description="Name of connected relational database")
    latency_ms: Optional[float] = Field(None, description="Connection latency in milliseconds")
    error: Optional[str] = Field(None, description="Error message if connection failed")


class HealthResponse(BaseModel):
    """
    System-wide health check response model.
    """
    status: str = Field(..., description="'ok' or 'degraded'")
    version: str = Field("1.0.0", description="API Service Version")
    database: DatabaseHealth


class QueryRequest(BaseModel):
    """
    Inbound natural language business query request.
    """
    query: str = Field(..., min_length=2, max_length=1000, description="Natural language question")
    conversation_id: Optional[str] = Field(None, description="Unique conversation session ID for persistent memory")
    database_id: Optional[str] = Field(None, description="Target database ID (defaults to MySQL business_analytics)")


class VisualizationPayload(BaseModel):
    """
    Plotly visualization figure and layout specification.
    """
    type: str = Field(..., description="Chart type: bar, line, pie, area, kpi, table")
    figure: Dict[str, Any] = Field(..., description="Plotly figure JSON structure (data and layout)")
    title: Optional[str] = Field(None, description="Chart title")


class ForecastPayload(BaseModel):
    """
    Predictive time-series forecast results.
    """
    metric: str = Field(..., description="Forecasted metric name")
    time_column: str = Field(..., description="Time column name")
    horizon: int = Field(default=6, description="Number of forecasted future periods")
    predictions: List[Dict[str, Any]] = Field(default_factory=list, description="Array of future forecasted points")
    confidence_intervals: Optional[Dict[str, Any]] = Field(None, description="80% and 95% confidence intervals")
    figure: Optional[Dict[str, Any]] = Field(None, description="Plotly figure combining historical and forecast series")


class QueryResponse(BaseModel):
    """
    Outbound response with natural language answer, SQL, data, insights, charts, and forecasts.
    """
    conversation_id: str
    question: str
    answer: str
    sql: Optional[str] = None
    data: List[Dict[str, Any]] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    visualization: Optional[VisualizationPayload] = None
    forecast: Optional[ForecastPayload] = None
    execution_time_ms: float = Field(default=0.0)
    error: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """
    Full conversation session turn history.
    """
    conversation_id: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
