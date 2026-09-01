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
    <div className={`py-6 px-4 sm:px-8 flex ${isUser ? "bg-[#0A0E18]/40" : "bg-[#0D1322]/80 border-y border-[#182236]"}`}>
      <div className="max-w-4xl mx-auto w-full flex space-x-4">
        {/* Avatar */}
        <div className="shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <User className="w-4 h-4" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-emerald-400 p-0.5 shadow-md shadow-indigo-500/20">
              <div className="w-full h-full bg-[#0B0F19] rounded-[6px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0 space-y-3">
          {/* Header & Timestamp */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-gray-200">
              {isUser ? "You" : "AI Data Analyst"}
            </span>
            <span className="text-[10px] text-gray-500">{message.timestamp}</span>
          </div>

          {/* User Message Text */}
          {isUser && (
            <p className="text-sm text-gray-200 leading-relaxed font-normal">
              {message.content}
            </p>
          )}

          {/* Assistant Loading State */}
          {loading && (
            <div className="flex items-center space-x-3 py-4 text-indigo-400 text-xs">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              <span className="font-medium animate-pulse">
                Analyzing query with LangGraph Multi-Agent pipeline...
              </span>
            </div>
          )}

          {/* Assistant Response Content */}
          {!isUser && !loading && response && (
            <div className="space-y-3">
              {/* Natural Language Answer / Summary */}
              {response.answer && (
                <div className="prose prose-invert prose-sm max-w-none text-gray-200 leading-relaxed text-sm">
                  <ReactMarkdown>{response.answer}</ReactMarkdown>
                </div>
              )}

              {/* Error Callout if any */}
              {response.error && (
                <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
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
                <div className="my-3 p-4 rounded-xl bg-[#111C30]/70 border border-indigo-900/30">
                  <div className="flex items-center space-x-2 text-xs font-semibold text-amber-300 mb-2">
                    <Lightbulb className="w-4 h-4 text-amber-400" />
                    <span>Executive Insights</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-gray-300">
                    {response.insights.map((insight, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>{insight}</span>
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
