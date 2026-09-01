"""
Result Analysis Agent for Persistent AI Data Analyst.
Computes numerical summaries, statistical patterns, period-over-period differences,
and provides grounded business explanations from tabular query results.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prompts.insight_prompts import ANALYSIS_SYSTEM_PROMPT
from app.services.llm_service import generate_structured_output
from app.utils.logger import logger


class AnalysisOutput(BaseModel):
    """
    Structured analytical explanation of SQL results.
    """
    summary: str = Field(..., description="High-level natural language summary of query results")
    key_findings: List[str] = Field(default_factory=list, description="Specific numerical observations and comparisons")
    statistical_metrics: Dict[str, Any] = Field(default_factory=dict, description="Computed statistics (total, average, max, min, change)")
    trend_direction: Optional[str] = Field(None, description="Overall trajectory: 'growth', 'decline', 'stable', or 'mixed'")


class ResultAnalysisAgent:
    """
    Analyzes SQL query result tables and produces grounded explanations.
    """

    @classmethod
    def analyze(
        cls,
        user_query: str,
        sql_query: str,
        data: List[Dict[str, Any]],
        columns: List[str],
    ) -> AnalysisOutput:
        """
        Analyze SQL query results and extract patterns.
        """
        if not data:
            return AnalysisOutput(
                summary="No records were returned matching your criteria.",
                key_findings=["Query executed successfully but yielded zero matching rows."],
                statistical_metrics={"row_count": 0},
                trend_direction="stable",
            )

        # Truncate sample data if too large for prompt
        sample_rows = data[:25]
        data_preview = f"COLUMNS: {columns}\nROWS ({len(data)} total, showing first {len(sample_rows)}):\n{sample_rows}"

        prompt = (
            f"{ANALYSIS_SYSTEM_PROMPT}\n\n"
            f"USER QUESTION:\n\"{user_query}\"\n\n"
            f"EXECUTED SQL:\n{sql_query}\n\n"
            f"QUERY RESULTS DATA:\n{data_preview}\n\n"
            "Analyze the data and provide a concise, data-grounded summary, key numerical findings, and computed metrics."
        )

        try:
            logger.info(f"Analyzing {len(data)} query result rows...")
            output: AnalysisOutput = generate_structured_output(
                prompt=prompt,
                schema=AnalysisOutput,
                temperature=0.0,
            )
            return output

        except Exception as e:
            logger.error(f"ResultAnalysisAgent error: {e}. Generating rule-based summary.")
            return AnalysisOutput(
                summary=f"The query returned {len(data)} records across {len(columns)} columns.",
                key_findings=[f"Top row: {data[0]}" if data else "Empty result"],
                statistical_metrics={"row_count": len(data)},
                trend_direction="mixed",
            )
