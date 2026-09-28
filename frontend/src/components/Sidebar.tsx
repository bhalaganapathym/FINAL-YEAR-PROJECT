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
  onNewConversation,
  onSelectConversation,
  dbStatus,
  databases,
  activeDatabaseId,
  onSelectDatabase,
  onOpenUploadModal,
}) => {
  return (
    <aside className="w-80 bg-[#FFFDF5] border-r-4 border-black flex flex-col h-screen select-none z-20">
      {/* Brand Header */}
      <div className="p-5 border-b-4 border-black bg-[#FFD93D] flex items-center space-x-3">
        <div className="w-11 h-11 bg-white border-3 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center rotate-[-2deg]">
          <Sparkles className="w-6 h-6 text-black stroke-[3px]" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <h1 className="font-black text-sm text-black tracking-tight uppercase">
              AI DATA ANALYST
            </h1>
            <span className="text-[10px] uppercase font-black px-1.5 py-0.5 bg-[#FF6B6B] text-white border-2 border-black rotate-[2deg]">
              2.0
            </span>
          </div>
          <p className="text-[11px] text-black font-bold uppercase tracking-wider">
            Conversational BI
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 space-y-3 border-b-4 border-black bg-white">
        <button
          onClick={onNewConversation}
          className="w-full py-3 px-4 bg-[#FF6B6B] hover:bg-[#ff5252] text-white font-black text-xs uppercase tracking-wider border-4 border-black shadow-[4px_4px_0px_0px_#000] flex items-center justify-center space-x-2 neo-btn"
        >
          <Plus className="w-4 h-4 stroke-[3px]" />
          <span>New Analysis</span>
        </button>

        <button
          onClick={onOpenUploadModal}
          className="w-full py-2.5 px-3 bg-[#C4B5FD] hover:bg-[#b8a6fc] text-black font-black text-xs uppercase tracking-wider border-3 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center space-x-2 neo-btn"
        >
          <Upload className="w-4 h-4 stroke-[3px]" />
          <span>Upload Dataset / DB</span>
        </button>
      </div>

      {/* Active Database Selector */}
      <div className="p-4 border-b-4 border-black bg-[#FFFDF5]">
        <div className="text-[11px] font-black uppercase text-black mb-2 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <HardDrive className="w-4 h-4 stroke-[3px]" />
            Active Source
          </span>
          <span className="text-[10px] px-1.5 py-0.5 bg-[#FFD93D] border-2 border-black font-black">
            {databases.length} DB(s)
          </span>
        </div>
        <select
          value={activeDatabaseId}
          onChange={(e) => onSelectDatabase(e.target.value)}
          className="w-full py-2 px-3 bg-white border-3 border-black text-xs font-bold text-black focus:bg-[#FFD93D] focus:outline-none shadow-[3px_3px_0px_0px_#000] cursor-pointer truncate"
        >
          {databases.map((db) => (
            <option key={db.database_id} value={db.database_id}>
              {db.name} ({db.tables_count} tbls)
            </option>
          ))}
        </select>
      </div>

      {/* Session History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <div className="px-2 py-1 text-[11px] font-black uppercase tracking-wider text-black flex items-center justify-between">
          <span>Recent Sessions</span>
        </div>
        {conversations.length === 0 ? (
          <div className="p-6 text-center text-xs font-bold text-gray-600 bg-white border-3 border-dashed border-black">
            NO PAST SESSIONS YET.
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === currentId;
            return (
              <button
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full text-left p-2.5 text-xs font-bold flex items-center space-x-2.5 border-3 border-black transition-all neo-btn ${
                  isActive
                    ? "bg-[#FFD93D] text-black shadow-[4px_4px_0px_0px_#000] -translate-y-0.5"
                    : "bg-white text-black hover:bg-[#FFFDF5] shadow-[2px_2px_0px_0px_#000]"
                }`}
              >
                <MessageSquare className="w-4 h-4 shrink-0 stroke-[2.5px]" />
                <span className="truncate flex-1 uppercase text-[11px]">
                  {conv.title || "Untitled Session"}
                </span>
              </button>
            );
          })
        )}
      </div>

      {/* Capabilities Overview */}
      <div className="p-3 mx-3 my-2 bg-[#C4B5FD] border-3 border-black shadow-[3px_3px_0px_0px_#000] text-xs">
        <div className="font-black uppercase text-black flex items-center gap-1.5 text-[11px] mb-1">
          <BarChart3 className="w-4 h-4 stroke-[3px]" />
          Multi-Agent System
        </div>
        <div className="text-black font-bold space-y-1 text-[10px]">
          <div>• 10 Stateful LangGraph Nodes</div>
          <div>• Nixtla Statsforecast AutoARIMA</div>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-3 border-t-4 border-black bg-white flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 stroke-[3px]" />
          <span className="text-black font-black uppercase text-[11px]">Engine</span>
        </div>
        <div className="flex items-center space-x-1.5">
          {dbStatus.connected ? (
            <span className="px-2 py-0.5 bg-[#10B981] text-white border-2 border-black font-black text-[10px] uppercase shadow-[2px_2px_0px_0px_#000] flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 stroke-[3px]" />
              ONLINE {dbStatus.latency ? `(${dbStatus.latency}ms)` : ""}
            </span>
          ) : (
            <span className="px-2 py-0.5 bg-[#FF6B6B] text-white border-2 border-black font-black text-[10px] uppercase shadow-[2px_2px_0px_0px_#000] flex items-center gap-1">
              <AlertCircle className="w-3 h-3 stroke-[3px]" />
              OFFLINE
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};
