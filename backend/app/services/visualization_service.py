"""
Plotly Visualization Service for Persistent AI Data Analyst.
Builds interactive Plotly chart specifications:
- Bar Charts (Rankings & categorical comparisons)
- Line Charts (Time-series trends)
- Pie / Donut Charts (Market share & part-to-whole)
- Area Charts (Cumulative metrics)
- KPI Cards (Single metric aggregates)
- Tables (Detailed listings)
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from app.utils.logger import logger

# Premium Plotly color palette (Tailored Slate/Indigo/Teal/Rose)
COLOR_PALETTE = [
    "#6366F1", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#3B82F6", "#F97316", "#06B6D4"
]

DARK_LAYOUT_TEMPLATE = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#F3F4F6", "size": 12},
    "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    "hovermode": "closest",
    "autosize": True,
}


class VisualizationService:
    """
    Constructs frontend-friendly Plotly figure specifications.
    """

    @classmethod
    def create_figure(
        cls,
        chart_type: str,
        data: List[Dict[str, Any]],
        x_col: str,
        y_col: str,
        title: Optional[str] = None,
        color_col: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Plotly figure dictionary {data: [...], layout: {...}}.
        """
        if not data:
            return {"data": [], "layout": {"title": "No Data Available"}}

        chart_type = chart_type.lower()
        title_text = title or f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}"

        layout = {
            **DARK_LAYOUT_TEMPLATE,
            "title": {"text": title_text, "font": {"size": 16, "color": "#FFFFFF"}},
            "xaxis": {
                "title": x_col.replace("_", " ").title(),
                "gridcolor": "#374151",
                "zerolinecolor": "#4B5563",
            },
            "yaxis": {
                "title": y_col.replace("_", " ").title(),
                "gridcolor": "#374151",
                "zerolinecolor": "#4B5563",
            },
        }

        # Extract values
        x_vals = [row.get(x_col) for row in data]
        y_vals = [row.get(y_col) for row in data]

        if chart_type == "line":
            trace = {
                "type": "scatter",
                "mode": "lines+markers",
                "x": x_vals,
                "y": y_vals,
                "name": y_col.replace("_", " ").title(),
                "line": {"color": "#6366F1", "width": 3, "shape": "spline"},
                "marker": {"size": 6, "color": "#818CF8"},
            }
            return {"data": [trace], "layout": layout}

        elif chart_type == "area":
            trace = {
                "type": "scatter",
                "mode": "lines",
                "fill": "tozeroy",
                "x": x_vals,
                "y": y_vals,
                "name": y_col.replace("_", " ").title(),
                "line": {"color": "#10B981", "width": 2},
                "fillcolor": "rgba(16, 185, 129, 0.2)",
            }
            return {"data": [trace], "layout": layout}

        elif chart_type == "pie":
            trace = {
                "type": "pie",
                "labels": x_vals,
                "values": y_vals,
                "hole": 0.4,
                "marker": {"colors": COLOR_PALETTE},
                "textinfo": "label+percent",
                "hoverinfo": "label+value+percent",
            }
            pie_layout = {
                **DARK_LAYOUT_TEMPLATE,
                "title": {"text": title_text, "font": {"size": 16, "color": "#FFFFFF"}},
            }
            return {"data": [trace], "layout": pie_layout}

        elif chart_type == "kpi":
            val = y_vals[0] if y_vals else (x_vals[0] if x_vals else 0)
            trace = {
                "type": "indicator",
                "mode": "number",
                "value": val,
                "title": {"text": title_text, "font": {"size": 14, "color": "#9CA3AF"}},
                "number": {"font": {"size": 36, "color": "#10B981"}},
            }
            kpi_layout = {
                **DARK_LAYOUT_TEMPLATE,
                "margin": {"l": 20, "r": 20, "t": 30, "b": 20},
                "height": 200,
            }
            return {"data": [trace], "layout": kpi_layout}

        else:
            # Default: Bar Chart
            trace = {
                "type": "bar",
                "x": x_vals,
                "y": y_vals,
                "name": y_col.replace("_", " ").title(),
                "marker": {
                    "color": COLOR_PALETTE[0],
                    "opacity": 0.9,
                    "line": {"color": "#818CF8", "width": 1},
                },
            }
            return {"data": [trace], "layout": layout}
