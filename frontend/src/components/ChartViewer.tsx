import React, { Suspense, lazy } from "react";
import { BarChart3, Loader2 } from "lucide-react";
import { VisualizationPayload } from "../types";

const Plot = lazy(() => import("react-plotly.js"));

interface ChartViewerProps {
  visualization?: VisualizationPayload;
}

export const ChartViewer: React.FC<ChartViewerProps> = ({ visualization }) => {
  if (!visualization || !visualization.figure) {
    return null;
  }

  const { figure, title, type } = visualization;

  return (
    <div className="border-4 border-black shadow-[8px_8px_0px_0px_#000] bg-white overflow-hidden my-4">
      {/* Chart Header */}
      <div className="px-4 py-2.5 bg-[#FF6B6B] text-white font-black text-xs uppercase tracking-wider border-b-4 border-black flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 stroke-[3px]" />
          <span>{title || "INTERACTIVE VISUALIZATION"}</span>
        </div>
        <span className="px-2 py-0.5 bg-[#FFD93D] text-black border-2 border-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000]">
          {type?.toUpperCase() || "PLOT"}
        </span>
      </div>

      {/* Plotly Canvas */}
      <div className="p-3 w-full bg-white flex items-center justify-center min-h-[340px]">
        <Suspense
          fallback={
            <div className="flex flex-col items-center justify-center p-8 space-y-2 text-black">
              <Loader2 className="w-6 h-6 animate-spin stroke-[3px]" />
              <span className="text-xs font-black uppercase">Rendering Neo Chart...</span>
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
            style={{ width: "100%", height: "340px" }}
            config={{
              responsive: true,
              displayModeBar: false,
            }}
          />
        </Suspense>
      </div>
    </div>
  );
};
