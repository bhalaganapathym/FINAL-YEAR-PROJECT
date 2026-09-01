"""
Visualization Agent for Persistent AI Data Analyst.
Inspects query results and intent to automatically determine optimal chart types:
- Time series (dates, months, years) -> Line / Area Chart
- Categorical comparisons & rankings -> Bar Chart
- Proportions & distributions (< 7 categories) -> Pie / Donut Chart
- Single scalar metric -> KPI Card
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.services.visualization_service import VisualizationService
from app.utils.logger import logger


class VisualizationDecision(BaseModel):
    """
    Visualization decision metadata.
    """
    should_visualize: bool = Field(..., description="True if data is suitable for graphical display")
    chart_type: str = Field(default="bar", description="bar, line, pie, area, kpi, table")
    x_axis_column: Optional[str] = Field(None, description="Dimension or time column name for X axis")
    y_axis_column: Optional[str] = Field(None, description="Numeric metric column name for Y axis")
    title: Optional[str] = Field(None, description="Clean chart title")
    reasoning: Optional[str] = Field(None, description="Explanation for chart selection")


class VisualizationAgent:
    """
    Selects chart type and prepares Plotly figure payload.
    """

    TIME_COLUMN_KEYWORDS = {"date", "month", "month_name", "year", "quarter", "day", "week", "created_at"}

    @classmethod
    def _is_numeric(cls, val: Any) -> bool:
        return isinstance(val, (int, float)) and not isinstance(val, bool)

    @classmethod
    def select_chart_type(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        user_query: Optional[str] = None,
    ) -> VisualizationDecision:
        """
        Heuristic and structural chart type determination.
        """
        if not data or len(columns) < 1:
            return VisualizationDecision(
                should_visualize=False,
                chart_type="table",
                reasoning="Empty data"
            )

        # Single row, single column -> KPI Card
        if len(data) == 1 and len(columns) == 1:
            col = columns[0]
            val = data[0].get(col)
            if cls._is_numeric(val):
                return VisualizationDecision(
                    should_visualize=True,
                    chart_type="kpi",
                    x_axis_column=col,
                    y_axis_column=col,
                    title=col.replace("_", " ").title(),
                    reasoning="Single scalar metric display."
                )

        # Identify numerical columns and categorical/time columns
        first_row = data[0]
        numeric_cols = [c for c in columns if cls._is_numeric(first_row.get(c))]
        dim_cols = [c for c in columns if c not in numeric_cols]

        if not numeric_cols:
            return VisualizationDecision(
                should_visualize=False,
                chart_type="table",
                reasoning="No numeric metric column present for plotting."
            )

        y_col = numeric_cols[0]
        x_col = dim_cols[0] if dim_cols else (columns[0] if columns[0] != y_col else columns[-1])

        # Detect time-series
        is_time_series = any(
            kw in x_col.lower() or (isinstance(first_row.get(x_col), str) and re.match(r"^\d{4}-\d{2}", str(first_row.get(x_col))))
            for kw in cls.TIME_COLUMN_KEYWORDS
        )

        query_str = (user_query or "").lower()

        if "pie" in query_str or "share" in query_str or "distribution" in query_str:
            if 1 < len(data) <= 8:
                return VisualizationDecision(
                    should_visualize=True,
                    chart_type="pie",
                    x_axis_column=x_col,
                    y_axis_column=y_col,
                    title=f"{y_col.replace('_', ' ').title()} Share by {x_col.replace('_', ' ').title()}",
                    reasoning="Part-to-whole distribution requested."
                )

        if is_time_series:
            chart_type = "area" if "cumulative" in query_str or "area" in query_str else "line"
            return VisualizationDecision(
                should_visualize=True,
                chart_type=chart_type,
                x_axis_column=x_col,
                y_axis_column=y_col,
                title=f"{y_col.replace('_', ' ').title()} Trend over {x_col.replace('_', ' ').title()}",
                reasoning="Time-series sequential pattern detected."
            )

        # Default multi-row categorical -> Bar Chart
        return VisualizationDecision(
            should_visualize=True,
            chart_type="bar",
            x_axis_column=x_col,
            y_axis_column=y_col,
            title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
            reasoning="Categorical comparison and ranking."
        )

    @classmethod
    def generate_visualization(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        user_query: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate data and return Plotly visualization payload if appropriate.
        """
        decision = cls.select_chart_type(data, columns, user_query)

        if not decision.should_visualize or not decision.x_axis_column or not decision.y_axis_column:
            return None

        try:
            fig = VisualizationService.create_figure(
                chart_type=decision.chart_type,
                data=data,
                x_col=decision.x_axis_column,
                y_col=decision.y_axis_column,
                title=decision.title,
            )
            return {
                "type": decision.chart_type,
                "figure": fig,
                "title": decision.title,
            }
        except Exception as e:
            logger.error(f"Visualization generation error: {e}")
            return None
