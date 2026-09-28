import React from "react";
import ReactMarkdown from "react-markdown";
import { MessageItem } from "../types";
import { SqlViewer } from "./SqlViewer";
import { ChartViewer } from "./ChartViewer";
import { DataTable } from "./DataTable";
import { ForecastViewer } from "./ForecastViewer";
import { Sparkles, User, Lightbulb, AlertTriangle, Loader2 } from "lucide-react";

interface ChatMessageProps {
  message: MessageItem;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";
  const { response, loading } = message;

  return (
    <div className={`py-5 px-4 sm:px-8 flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`w-full max-w-4xl flex space-x-3.5 ${isUser ? "flex-row-reverse space-x-reverse" : "flex-row"}`}>
        {/* Avatar */}
        <div className="shrink-0 mt-1">
          {isUser ? (
            <div className="w-10 h-10 bg-[#FF6B6B] border-3 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center text-white rotate-[2deg]">
              <User className="w-5 h-5 stroke-[3px]" />
            </div>
          ) : (
            <div className="w-10 h-10 bg-[#FFD93D] border-3 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center text-black rotate-[-2deg]">
              <Sparkles className="w-5 h-5 stroke-[3px]" />
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0">
          {/* Header & Timestamp */}
          <div className={`flex items-center space-x-2 mb-1.5 ${isUser ? "justify-end" : "justify-start"}`}>
            <span className="text-xs font-black uppercase text-black">
              {isUser ? "YOU" : "AI DATA ANALYST"}
            </span>
            <span className="text-[10px] font-mono font-bold bg-white px-1.5 py-0.5 border border-black text-black">
              {message.timestamp}
            </span>
          </div>

          {/* User Message Text */}
          {isUser && (
            <div className="p-4 bg-[#FFD93D] border-4 border-black shadow-[6px_6px_0px_0px_#000] text-black font-bold text-sm leading-relaxed max-w-2xl ml-auto">
              {message.content}
            </div>
          )}

          {/* Assistant Loading State */}
          {loading && (
            <div className="p-5 bg-white border-4 border-black shadow-[6px_6px_0px_0px_#000] flex items-center space-x-3 text-black">
              <Loader2 className="w-5 h-5 animate-spin stroke-[3px] text-[#FF6B6B]" />
              <span className="text-xs font-black uppercase tracking-wider">
                Analyzing query with LangGraph Multi-Agent pipeline...
              </span>
            </div>
          )}

          {/* Assistant Response Card */}
          {!isUser && !loading && response && (
            <div className="space-y-4">
              {/* Natural Language Answer / Summary */}
              {response.answer && (
                <div className="p-5 bg-white border-4 border-black shadow-[6px_6px_0px_0px_#000] text-black leading-relaxed text-sm font-bold">
                  <div className="prose max-w-none text-black font-bold">
                    <ReactMarkdown>{response.answer}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Error Callout if any */}
              {response.error && (
                <div className="p-4 bg-[#FF6B6B] border-4 border-black shadow-[6px_6px_0px_0px_#000] text-white text-xs font-black uppercase flex items-start space-x-2.5">
                  <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 stroke-[3px]" />
                  <span>{response.error}</span>
                </div>
              )}

              {/* SQL Viewer */}
              {response.sql && (
                <SqlViewer
                  sql={response.sql}
                  executionTimeMs={response.execution_time_ms}
                  rowCount={response.data?.length}
                />
              )}

              {/* Business Insights Bullets */}
              {response.insights && response.insights.length > 0 && (
                <div className="p-4 bg-[#C4B5FD] border-4 border-black shadow-[6px_6px_0px_0px_#000]">
                  <div className="flex items-center space-x-2 text-xs font-black uppercase text-black mb-2.5">
                    <div className="p-1 bg-white border-2 border-black">
                      <Lightbulb className="w-4 h-4 stroke-[3px] text-black" />
                    </div>
                    <span>EXECUTIVE BUSINESS INSIGHTS</span>
                  </div>
                  <ul className="space-y-2 text-xs font-bold text-black">
                    {response.insights.map((insight, idx) => (
                      <li key={idx} className="flex items-start space-x-2 bg-white/60 p-2 border-2 border-black">
                        <span className="text-black font-black">•</span>
                        <span className="leading-relaxed">{insight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Visualization Chart */}
              {response.visualization && (
                <ChartViewer visualization={response.visualization} />
              )}

              {/* Forecast Viewer */}
              {response.forecast && (
                <ForecastViewer forecast={response.forecast} />
              )}

              {/* Data Table */}
              {response.data && response.data.length > 0 && response.columns && (
                <DataTable columns={response.columns} data={response.data} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
