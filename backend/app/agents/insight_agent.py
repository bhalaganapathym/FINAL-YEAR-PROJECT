"""
Business Insight Agent for Persistent AI Data Analyst.
Transforms raw query results and statistical analysis into concise, executive-level business insights.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prompts.insight_prompts import INSIGHT_SYSTEM_PROMPT
from app.services.llm_service import generate_structured_output
from app.utils.logger import logger


class InsightsOutput(BaseModel):
    """
    Structured business insights list.
    """
    insights: List[str] = Field(
        ...,
        description="List of 3 to 5 concise, actionable business insight bullet points"
    )
    executive_summary: Optional[str] = Field(
        None,
        description="One-sentence executive headline"
    )


class InsightAgent:
    """
    Produces executive business insights grounded in actual query execution data.
    """

    @classmethod
    def generate_insights(
        cls,
        user_query: str,
        analysis_summary: str,
        data: List[Dict[str, Any]],
        columns: List[str],
    ) -> List[str]:
        """
        Generate bulleted business insights from analysis and data.
        """
        if not data:
            return ["No data available to generate insights."]

        sample_rows = data[:20]
        prompt = (
            f"{INSIGHT_SYSTEM_PROMPT}\n\n"
            f"USER QUESTION:\n\"{user_query}\"\n\n"
            f"ANALYSIS SUMMARY:\n{analysis_summary}\n\n"
            f"SAMPLE DATA ({len(data)} total rows):\n{sample_rows}\n\n"
            "Extract 3 to 5 clear, high-impact business insight bullet points."
        )

        try:
            logger.info("Generating business insights from query data...")
            output: InsightsOutput = generate_structured_output(
                prompt=prompt,
                schema=InsightsOutput,
                temperature=0.2,
            )
            return output.insights

        except Exception as e:
            logger.error(f"InsightAgent error: {e}. Generating default insight bullet.")
            return [
                f"Query completed with {len(data)} records returned.",
                f"Primary metric displayed across {len(columns)} dimensions.",
            ]
