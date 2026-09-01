"""
Time-Series Forecasting Agent for Persistent AI Data Analyst.
Utilizes Nixtla's statsforecast library (AutoARIMA, AutoETS) with dynamic adaptation
to produce:
- Point forecasts across requested forecast horizon
- 80% and 95% confidence intervals
- Interactive Plotly visualization combining historical series + prediction cones
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, SeasonalNaive, Naive
from app.utils.logger import logger


class ForecastAgent:
    """
    Time-Series Forecasting Engine powered by statsforecast.
    """

    TIME_COL_KEYWORDS = ["date", "month", "sale_date", "order_date", "ds", "time", "forecast_month"]

    @classmethod
    def _detect_time_and_metric_columns(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Identify time column and target numeric column.
        """
        if not data or not columns:
            return None, None

        first_row = data[0]

        # 1. Detect time column
        time_col = None
        for col in columns:
            col_lower = col.lower()
            if any(k in col_lower for k in cls.TIME_COL_KEYWORDS):
                time_col = col
                break

        # Fallback: check if first row value parses as date
        if not time_col:
            for col in columns:
                val = str(first_row.get(col, ""))
                if re.match(r"^\d{4}[-/]\d{1,2}", val):
                    time_col = col
                    break

        # 2. Detect numeric metric column
        metric_col = None
        for col in columns:
            if col == time_col:
                continue
            val = first_row.get(col)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                metric_col = col
                break

        return time_col, metric_col

    @classmethod
    def run_forecast(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        horizon: int = 6,
        user_query: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Train AutoARIMA/AutoETS model on historical data and return future forecast with confidence ribbons.
        """
        time_col, metric_col = cls._detect_time_and_metric_columns(data, columns)

        if not time_col or not metric_col:
            logger.warning(f"Forecasting skipped: could not identify time ({time_col}) and metric ({metric_col}) columns.")
            return None

        try:
            # Prepare DataFrame
            df = pd.DataFrame(data)
            df = df.dropna(subset=[time_col, metric_col])

            # Handle date parsing
            df["ds"] = pd.to_datetime(df[time_col], errors="coerce")
            df = df.dropna(subset=["ds"])

            df["y"] = pd.to_numeric(df[metric_col], errors="coerce")
            df = df.dropna(subset=["y"])

            # Sort chronologically and aggregate by frequency
            df = df.sort_values("ds")
            df = df.groupby(pd.Grouper(key="ds", freq="MS"))["y"].sum().reset_index()
            df = df[df["y"] > 0]

            n_samples = len(df)
            if n_samples < 2:
                logger.warning("Insufficient data points for forecasting (< 2 observations).")
                return None

            df["unique_id"] = "metric_series"
            input_df = df[["unique_id", "ds", "y"]].copy()

            logger.info(f"Fitting statsforecast on {n_samples} periods with horizon={horizon}...")

            # Dynamically select models based on sample length
            if n_samples >= 24:
                models = [AutoARIMA(season_length=12), AutoETS(season_length=12)]
            elif n_samples >= 8:
                models = [AutoARIMA(season_length=min(4, n_samples // 2)), AutoETS(season_length=min(4, n_samples // 2))]
            else:
                # Small series fallback
                models = [AutoARIMA(season_length=1), AutoETS(season_length=1), Naive()]

            sf = StatsForecast(
                models=models,
                freq="MS",
                n_jobs=1,
            )

            sf.fit(input_df)
            forecast_df = sf.predict(h=horizon, level=[80, 95])

            # Extract forecast values
            forecast_records = []
            available_cols = [c for c in ["AutoARIMA", "AutoETS", "Naive"] if c in forecast_df.columns]
            selected_model = available_cols[0] if available_cols else forecast_df.columns[2]

            for _, row in forecast_df.iterrows():
                ds_str = pd.to_datetime(row["ds"]).strftime("%Y-%m-%d")
                predicted_val = float(row[selected_model])
                lo_80 = float(row.get(f"{selected_model}-lo-80", predicted_val * 0.88))
                hi_80 = float(row.get(f"{selected_model}-hi-80", predicted_val * 1.12))
                lo_95 = float(row.get(f"{selected_model}-lo-95", predicted_val * 0.78))
                hi_95 = float(row.get(f"{selected_model}-hi-95", predicted_val * 1.22))

                forecast_records.append({
                    "date": ds_str,
                    "predicted_value": round(max(0.0, predicted_val), 2),
                    "lower_80": round(max(0.0, lo_80), 2),
                    "upper_80": round(max(0.0, hi_80), 2),
                    "lower_95": round(max(0.0, lo_95), 2),
                    "upper_95": round(max(0.0, hi_95), 2),
                })

            # Build Plotly Forecast Figure
            hist_x = [d.strftime("%Y-%m-%d") for d in df["ds"]]
            hist_y = df["y"].tolist()

            fc_x = [r["date"] for r in forecast_records]
            fc_y = [r["predicted_value"] for r in forecast_records]
            fc_hi_95 = [r["upper_95"] for r in forecast_records]
            fc_lo_95 = [r["lower_95"] for r in forecast_records]

            # Connect historical to forecast seamlessly
            join_x = [hist_x[-1]] + fc_x
            join_y = [hist_y[-1]] + fc_y
            join_hi_95 = [hist_y[-1]] + fc_hi_95
            join_lo_95 = [hist_y[-1]] + fc_lo_95

            traces = [
                # Historical Line
                {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": hist_x,
                    "y": hist_y,
                    "name": f"Historical {metric_col.replace('_', ' ').title()}",
                    "line": {"color": "#6366F1", "width": 3},
                    "marker": {"size": 6, "color": "#818CF8"},
                },
                # 95% Upper Bound
                {
                    "type": "scatter",
                    "mode": "lines",
                    "x": join_x,
                    "y": join_hi_95,
                    "name": "95% Upper Interval",
                    "line": {"color": "rgba(16, 185, 129, 0)", "width": 0},
                    "showlegend": False,
                },
                # 95% Confidence Ribbon (Fill to Lower)
                {
                    "type": "scatter",
                    "mode": "lines",
                    "x": join_x,
                    "y": join_lo_95,
                    "name": "95% Confidence Interval",
                    "fill": "tonexty",
                    "fillcolor": "rgba(16, 185, 129, 0.15)",
                    "line": {"color": "rgba(16, 185, 129, 0)", "width": 0},
                },
                # Forecasted Line
                {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": join_x,
                    "y": join_y,
                    "name": f"Predicted {metric_col.replace('_', ' ').title()} ({selected_model})",
                    "line": {"color": "#10B981", "width": 3, "dash": "dash"},
                    "marker": {"size": 6, "color": "#34D399"},
                },
            ]

            layout = {
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif", "color": "#F3F4F6", "size": 12},
                "title": {
                    "text": f"6-Month Predictive Forecast: {metric_col.replace('_', ' ').title()}",
                    "font": {"size": 16, "color": "#FFFFFF"}
                },
                "xaxis": {"title": "Month", "gridcolor": "#374151"},
                "yaxis": {"title": metric_col.replace('_', ' ').title(), "gridcolor": "#374151"},
                "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
                "autosize": True,
            }

            figure = {"data": traces, "layout": layout}

            logger.info(f"Forecast successfully generated for horizon={horizon} periods.")

            return {
                "metric": metric_col,
                "time_column": time_col,
                "horizon": horizon,
                "predictions": forecast_records,
                "confidence_intervals": {"levels": [80, 95]},
                "figure": figure,
            }

        except Exception as e:
            logger.error(f"Forecasting model execution failed: {e}")
            return None
