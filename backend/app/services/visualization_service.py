"""
Plotly Visualization Service for Persistent AI Data Analyst.
Builds high-contrast Neo-Brutalist Plotly chart specifications:
- Bar Charts (Rankings & categorical comparisons)
- Line Charts (Time-series trends)
- Pie / Donut Charts (Market share & part-to-whole)
- Area Charts (Cumulative metrics)
- KPI Cards (Single metric aggregates)
- Tables (Detailed listings)
"""

from typing import Any, Dict, List, Optional
from app.utils.logger import logger

# Neo-Brutalist High-Saturation Color Palette
COLOR_PALETTE = [
    "#FF6B6B", "#FFD93D", "#8B5CF6", "#10B981", "#38BDF8",
    "#F97316", "#EC4899", "#A855F7", "#06B6D4", "#84CC16",
    "#D946EF", "#F43F5E", "#000000", "#6366F1", "#14B8A6"
]

NEO_LAYOUT_TEMPLATE = {
    "paper_bgcolor": "#FFFFFF",
    "plot_bgcolor": "#FFFDF5",
    "font": {"family": "Space Grotesk, sans-serif", "color": "#000000", "size": 13, "weight": 700},
    "margin": {"l": 60, "r": 40, "t": 60, "b": 60},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.3, "xanchor": "center", "x": 0.5, "font": {"color": "#000000"}},
    "hovermode": "closest",
    "autosize": True,
}


class VisualizationService:
    """
    Constructs frontend-friendly Neo-Brutalist Plotly figure specifications.
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
        title_text = (title or f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}").upper()

        layout = {
            **NEO_LAYOUT_TEMPLATE,
            "title": {
                "text": f"<b>{title_text}</b>",
                "font": {"size": 16, "color": "#000000", "family": "Space Grotesk, sans-serif"},
            },
            "xaxis": {
                "title": f"<b>{x_col.replace('_', ' ').upper()}</b>",
                "gridcolor": "#E5E7EB",
                "linecolor": "#000000",
                "linewidth": 3,
                "zerolinecolor": "#000000",
                "zerolinewidth": 2,
                "tickfont": {"color": "#000000", "size": 11, "family": "Space Grotesk, sans-serif"},
            },
            "yaxis": {
                "title": f"<b>{y_col.replace('_', ' ').upper()}</b>",
                "gridcolor": "#E5E7EB",
                "linecolor": "#000000",
                "linewidth": 3,
                "zerolinecolor": "#000000",
                "zerolinewidth": 2,
                "tickfont": {"color": "#000000", "size": 11, "family": "Space Grotesk, sans-serif"},
            },
        }

        x_vals = [row.get(x_col) for row in data]
        y_vals = [row.get(y_col) for row in data]

        if chart_type == "line":
            trace = {
                "type": "scatter",
                "mode": "lines+markers",
                "x": x_vals,
                "y": y_vals,
                "name": y_col.replace("_", " ").title(),
                "line": {"color": "#FF6B6B", "width": 4},
                "marker": {"size": 8, "color": "#000000", "line": {"color": "#FFD93D", "width": 2}},
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
                "line": {"color": "#10B981", "width": 3},
                "fillcolor": "rgba(16, 185, 129, 0.25)",
            }
            return {"data": [trace], "layout": layout}

        elif chart_type == "pie":
            colors = COLOR_PALETTE * ((len(x_vals) // len(COLOR_PALETTE)) + 1)
            trace = {
                "type": "pie",
                "labels": x_vals,
                "values": y_vals,
                "hole": 0.45,
                "marker": {
                    "colors": colors[:len(x_vals)],
                    "line": {"color": "#000000", "width": 3},
                },
                "textinfo": "percent" if len(x_vals) > 6 else "label+percent",
                "textposition": "inside" if len(x_vals) > 6 else "auto",
                "hoverinfo": "label+value+percent",
                "textfont": {"family": "Space Grotesk, sans-serif", "color": "#000000", "size": 12},
            }
            pie_layout = {
                **NEO_LAYOUT_TEMPLATE,
                "title": {"text": f"<b>{title_text}</b>", "font": {"size": 16, "color": "#000000"}},
                "showlegend": True,
            }
            return {"data": [trace], "layout": pie_layout}

        elif chart_type == "kpi":
            val = y_vals[0] if y_vals else (x_vals[0] if x_vals else 0)
            trace = {
                "type": "indicator",
                "mode": "number",
                "value": val,
                "title": {"text": f"<b>{title_text}</b>", "font": {"size": 16, "color": "#000000"}},
                "number": {"font": {"size": 42, "color": "#FF6B6B", "family": "Space Grotesk, sans-serif"}},
            }
            kpi_layout = {
                **NEO_LAYOUT_TEMPLATE,
                "margin": {"l": 30, "r": 30, "t": 40, "b": 30},
                "height": 220,
            }
            return {"data": [trace], "layout": kpi_layout}

        else:
            # Default: Bar Chart with thick black outline
            trace = {
                "type": "bar",
                "x": x_vals,
                "y": y_vals,
                "name": y_col.replace("_", " ").title(),
                "marker": {
                    "color": COLOR_PALETTE[0],
                    "line": {"color": "#000000", "width": 3},
                },
            }
            return {"data": [trace], "layout": layout}
