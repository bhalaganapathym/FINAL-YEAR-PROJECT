import React from "react";
import Plot from "react-plotly.js";
import { ForecastPayload } from "../types";
import { TrendingUp, Calendar } from "lucide-react";

interface ForecastViewerProps {
  forecast: ForecastPayload;
}

export const ForecastViewer: React.FC<ForecastViewerProps> = ({ forecast }) => {
  const { metric, horizon, predictions, figure } = forecast;

  if (!predictions || predictions.length === 0) {
    return null;
  }

  const layout = {
    ...(figure?.layout || {}),
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 50, r: 25, t: 40, b: 45 },
    font: {
      family: "Inter, system-ui, sans-serif",
      color: "#9CA3AF",
      size: 11,
    },
  };

  return (
    <div className="my-4 rounded-xl border border-emerald-900/40 bg-[#06151E]/80 p-4 backdrop-blur-md shadow-xl">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-300">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span>{horizon}-Month Predictive Forecast: {metric.replace(/_/g, " ").toUpperCase()}</span>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 text-[10px] border border-emerald-800/40 font-medium">
          AutoARIMA (80% & 95% CI)
        </span>
      </div>

      {/* Plotly Forecast Chart */}
      {figure && figure.data && (
        <div className="w-full h-80 min-h-[320px] mb-4">
          <Plot
            data={figure.data}
            layout={layout}
            config={{ responsive: true, displayModeBar: false }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%" }}
          />
        </div>
      )}

      {/* Future Values Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 pt-2 border-t border-[#1F2937]/50">
        {predictions.map((p, idx) => (
          <div key={idx} className="p-2.5 rounded-lg bg-[#0B1522] border border-[#1F2937] text-center">
            <div className="text-[10px] text-gray-400 flex items-center justify-center gap-1">
              <Calendar className="w-3 h-3 text-indigo-400" />
              {p.date}
            </div>
            <div className="text-sm font-bold text-emerald-400 mt-0.5">
              {p.predicted_value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </div>
            <div className="text-[9px] text-gray-500 mt-0.5">
              [{p.lower_95.toLocaleString(undefined, { maximumFractionDigits: 0 })} - {p.upper_95.toLocaleString(undefined, { maximumFractionDigits: 0 })}]
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
