import React from "react";
import Plot from "react-plotly.js";
import { VisualizationPayload } from "../types";
import { BarChart3 } from "lucide-react";

interface ChartViewerProps {
  visualization: VisualizationPayload;
}

export const ChartViewer: React.FC<ChartViewerProps> = ({ visualization }) => {
  const { figure, title } = visualization;

  if (!figure || !figure.data || figure.data.length === 0) {
    return null;
  }

  const layout = {
    ...figure.layout,
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 45, r: 25, t: 40, b: 45 },
    font: {
      family: "Inter, system-ui, sans-serif",
      color: "#9CA3AF",
      size: 11,
    },
  };

  return (
    <div className="my-4 rounded-xl border border-[#1F2937] bg-[#0E1526]/80 p-4 backdrop-blur-md shadow-xl">
      {title && (
        <div className="mb-3 flex items-center space-x-2 text-xs font-semibold text-gray-200">
          <BarChart3 className="w-4 h-4 text-indigo-400" />
          <span>{title}</span>
        </div>
      )}
      <div className="w-full h-80 min-h-[320px]">
        <Plot
          data={figure.data}
          layout={layout}
          config={{
            responsive: true,
            displayModeBar: false,
          }}
          useResizeHandler={true}
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </div>
  );
};
