import React from "react";
import { Plus, MessageSquare, Database, Sparkles, CheckCircle2, AlertCircle, BarChart3, Upload, HardDrive } from "lucide-react";
import { ConversationSummary, DatabaseSourceInfo } from "../types";

interface SidebarProps {
  conversations: ConversationSummary[];
  currentId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  dbStatus: { connected: boolean; status: string; latency?: number };
  databases: DatabaseSourceInfo[];
  activeDatabaseId: string;
  onSelectDatabase: (dbId: string) => void;
  onOpenUploadModal: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  currentId,
  onSelectConversation,
  onNewConversation,
  dbStatus,
  databases,
  activeDatabaseId,
  onSelectDatabase,
  onOpenUploadModal,
}) => {
  return (
    <aside className="w-72 bg-[#070B14] border-r border-[#1F2937] flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#1F2937] flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/20">
          <div className="w-full h-full bg-[#0B0F19] rounded-[10px] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
        <div>
          <h1 className="font-bold text-sm text-white tracking-wide flex items-center gap-1.5">
            AI Data Analyst
            <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-md border border-indigo-500/30">
              2.0
            </span>
          </h1>
          <p className="text-xs text-gray-400 font-medium">Conversational BI</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 space-y-2">
        <button
          onClick={onNewConversation}
          className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-indigo-600/20 active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>New Analysis</span>
        </button>

        <button
          onClick={onOpenUploadModal}
          className="w-full py-2 px-3 rounded-xl bg-[#111827] hover:bg-[#1E293B] border border-[#1F2937] text-indigo-300 hover:text-white font-medium text-xs flex items-center justify-center space-x-2 transition-all active:scale-[0.98]"
        >
          <Upload className="w-3.5 h-3.5 text-indigo-400" />
          <span>Upload Dataset / DB</span>
        </button>
      </div>

      {/* Active Databases / Data Sources Selector */}
      <div className="px-4 py-2 border-y border-[#1F2937]/60 bg-[#0A0E18]/50">
        <div className="text-[11px] font-semibold text-gray-400 mb-1.5 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
            Active Data Source
          </span>
          <span className="text-[10px] text-gray-500">{databases.length} source(s)</span>
        </div>
        <select
          value={activeDatabaseId}
          onChange={(e) => onSelectDatabase(e.target.value)}
          className="w-full py-1.5 px-2.5 bg-[#111827] border border-[#1F2937] rounded-lg text-xs text-gray-200 focus:outline-none focus:border-indigo-500 truncate"
        >
          {databases.map((db) => (
            <option key={db.database_id} value={db.database_id}>
              {db.name} ({db.tables_count} tbls)
            </option>
          ))}
        </select>
      </div>

      {/* Session History List */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1.5 py-3">
        <div className="px-3 py-1 text-[11px] font-semibold tracking-wider text-gray-500 uppercase">
          Recent Sessions
        </div>
        {conversations.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-gray-500">
            No past conversations yet.
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === currentId;
            return (
              <button
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-xs flex items-center space-x-3 transition-colors ${
                  isActive
                    ? "bg-indigo-950/50 text-indigo-300 border border-indigo-800/50 font-medium"
                    : "text-gray-400 hover:bg-[#111827] hover:text-gray-200"
                }`}
              >
                <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-indigo-400" : "text-gray-500"}`} />
                <span className="truncate flex-1">{conv.title || "Untitled Analysis"}</span>
              </button>
            );
          })
        )}
      </div>

      {/* Capabilities Overview */}
      <div className="p-3 mx-3 my-2 rounded-xl bg-[#111827]/70 border border-[#1F2937] text-xs space-y-1.5">
        <div className="font-semibold text-gray-300 flex items-center gap-1.5 text-[11px]">
          <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
          Multi-Source Engine
        </div>
        <div className="text-gray-400 space-y-1 text-[10px]">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Auto-converts CSV / Excel to SQL
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            Dynamic Schema Introspection
          </div>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-3.5 border-t border-[#1F2937] bg-[#0A0E17] flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-gray-400" />
          <span className="text-gray-300 font-medium text-[11px]">Engine</span>
        </div>
        <div className="flex items-center space-x-1.5">
          {dbStatus.connected ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium text-[11px]">
                Ready {dbStatus.latency ? `(${dbStatus.latency}ms)` : ""}
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
              <span className="text-rose-400 font-medium text-[11px]">Offline</span>
            </>
          )}
        </div>
      </div>
    </aside>
  );
};
