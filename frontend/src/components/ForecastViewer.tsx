import React, { Suspense, lazy } from "react";
import { TrendingUp, Loader2, Calendar } from "lucide-react";
import { ForecastPayload } from "../types";

const Plot = lazy(() => import("react-plotly.js"));

interface ForecastViewerProps {
  forecast?: ForecastPayload;
}

export const ForecastViewer: React.FC<ForecastViewerProps> = ({ forecast }) => {
  if (!forecast) return null;

  const { metric, horizon, predictions, figure } = forecast;

  return (
    <div className="border-4 border-black shadow-[8px_8px_0px_0px_#000] bg-white overflow-hidden my-4">
      {/* Header */}
      <div className="px-4 py-2.5 bg-[#10B981] text-white font-black text-xs uppercase tracking-wider border-b-4 border-black flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 stroke-[3px]" />
          <span>PREDICTIVE FORECAST: {metric?.toUpperCase() || "SALES"}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 bg-[#FFD93D] text-black border-2 border-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000]">
            {horizon || predictions?.length || 6} MONTHS
          </span>
          <span className="px-2 py-0.5 bg-white text-black border-2 border-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000]">
            AutoARIMA
          </span>
        </div>
      </div>

      {/* Plotly Forecast Chart */}
      {figure && (
        <div className="p-3 w-full bg-white flex items-center justify-center min-h-[320px] border-b-4 border-black">
          <Suspense
            fallback={
              <div className="flex flex-col items-center justify-center p-8 space-y-2 text-black">
                <Loader2 className="w-6 h-6 animate-spin stroke-[3px]" />
                <span className="text-xs font-black uppercase">Rendering Forecast...</span>
              </div>
            }
          >
            <Plot
              data={figure.data || []}
              layout={{
                ...figure.layout,
                autosize: true,
                paper_bgcolor: "#FFFFFF",
                plot_bgcolor: "#FFFDF5",
              }}
              useResizeHandler={true}
              style={{ width: "100%", height: "320px" }}
              config={{
                responsive: true,
                displayModeBar: false,
              }}
            />
          </Suspense>
        </div>
      )}

      {/* Prediction Cards Grid */}
      {predictions && predictions.length > 0 && (
        <div className="p-4 bg-[#FFFDF5]">
          <div className="text-[11px] font-black uppercase text-black mb-3 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 stroke-[3px]" />
            <span>Projected Monthly Values (80% / 95% Confidence Intervals)</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {predictions.map((p, idx) => (
              <div
                key={idx}
                className="p-3 bg-white border-3 border-black shadow-[3px_3px_0px_0px_#000] flex flex-col justify-between"
              >
                <div className="text-[11px] font-black uppercase text-black bg-[#FFD93D] px-1.5 py-0.5 border-2 border-black inline-block self-start mb-2 shadow-[1px_1px_0px_0px_#000]">
                  {p.date}
                </div>
                <div className="text-sm font-black text-black my-1">
                  ₹{p.predicted_value.toLocaleString("en-IN", { maximumFractionDigits: 1 })}
                </div>
                <div className="text-[9px] font-bold text-gray-700 mt-1 border-t-2 border-black pt-1">
                  95% CI: [{Math.round(p.lower_95).toLocaleString()} - {Math.round(p.upper_95).toLocaleString()}]
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
