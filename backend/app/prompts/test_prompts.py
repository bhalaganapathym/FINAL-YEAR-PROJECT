"""
Test prompt templates and Pydantic schemas for verifying Gemini structured output capabilities.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SimpleIntentTest(BaseModel):
    """
    Test schema for analytical intent extraction.
    """
    intent: str = Field(..., description="Classified intent (e.g., aggregation, ranking, comparison, forecasting)")
    metric: str = Field(..., description="Target business metric (e.g., sales, revenue, profit, quantity)")
    dimensions: List[str] = Field(default_factory=list, description="Dimensions to group by (e.g., region, month, category)")
    time_filter: Optional[str] = Field(None, description="Time filter mentioned in query (e.g., 2024, Q3, March)")
    requires_visualization: bool = Field(default=False, description="Whether the response benefits from a chart")
