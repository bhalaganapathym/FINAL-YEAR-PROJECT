import React, { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { api } from "./services/api";
import { MessageItem, ConversationSummary, QueryResponse, DatabaseSourceInfo } from "./types";
import { Sidebar } from "./components/Sidebar";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { DatabaseUploadModal } from "./components/DatabaseUploadModal";
import { Sparkles, Database, BarChart3, TrendingUp, Zap, HardDrive } from "lucide-react";

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentId, setCurrentId] = useState<string>(() => uuidv4());
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [dbStatus, setDbStatus] = useState<{ connected: boolean; status: string; latency?: number }>({
    connected: false,
    status: "checking",
  });

  const [databases, setDatabases] = useState<DatabaseSourceInfo[]>([]);
  const [activeDatabaseId, setActiveDatabaseId] = useState<string>("default");
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch health & databases list on mount
  useEffect(() => {
    const fetchStatusAndDatabases = async () => {
      const res = await api.checkHealth();
      setDbStatus({
        connected: res?.database?.connected || false,
        status: res?.status || "offline",
        latency: res?.database?.latency_ms,
      });

      const dbs = await api.listDatabases();
      setDatabases(dbs);
    };

    fetchStatusAndDatabases();
    const interval = setInterval(fetchStatusAndDatabases, 30000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleNewConversation = () => {
    const newId = uuidv4();
    setCurrentId(newId);
    setMessages([]);
  };

  const handleSelectConversation = (id: string) => {
    setCurrentId(id);
  };

  const handleDatabaseSelected = (db: DatabaseSourceInfo) => {
    setDatabases((prev) => {
      const exists = prev.find((d) => d.database_id === db.database_id);
      return exists ? prev : [db, ...prev];
    });
    setActiveDatabaseId(db.database_id);
    handleNewConversation();
  };

  const activeDbInfo = databases.find((d) => d.database_id === activeDatabaseId) || databases[0];

  const handleSendMessage = async (query: string) => {
    const userMsg: MessageItem = {
      id: uuidv4(),
      role: "user",
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const assistantMsgId = uuidv4();
    const placeholderAssistantMsg: MessageItem = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      loading: true,
    };

    setMessages((prev) => [...prev, userMsg, placeholderAssistantMsg]);
    setLoading(true);

    setConversations((prev) => {
      const exists = prev.find((c) => c.id === currentId);
      if (exists) {
        return prev.map((c) =>
          c.id === currentId ? { ...c, messageCount: c.messageCount + 1, lastUpdated: "Just now" } : c
        );
      }
      return [
        {
          id: currentId,
          title: query.slice(0, 30) + (query.length > 30 ? "..." : ""),
          lastUpdated: "Just now",
          messageCount: 1,
        },
        ...prev,
      ];
    });

    try {
      const response: QueryResponse = await api.sendQuery(query, currentId, activeDatabaseId);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                loading: false,
                content: response.answer,
                response: response,
              }
            : msg
        )
      );
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                loading: false,
                content: "Unable to connect to analytics engine.",
                response: {
                  conversation_id: currentId,
                  question: query,
                  answer: "Network error: Failed to reach backend.",
                  data: [],
                  columns: [],
                  insights: [],
                  execution_time_ms: 0,
                  error: err.message || "Network Error",
                },
              }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0B0F19] text-gray-100 overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar
        conversations={conversations}
        currentId={currentId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        dbStatus={dbStatus}
        databases={databases}
        activeDatabaseId={activeDatabaseId}
        onSelectDatabase={setActiveDatabaseId}
        onOpenUploadModal={() => setIsUploadModalOpen(true)}
      />

      {/* Main Chat Canvas */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Navbar */}
        <header className="h-14 border-b border-[#1F2937] bg-[#070B14]/80 backdrop-blur-md px-6 flex items-center justify-between z-10">
          <div className="flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-1.5 bg-emerald-950/40 text-emerald-300 px-3 py-1 rounded-lg border border-emerald-800/40 font-medium">
              <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
              <span>Target DB: {activeDbInfo?.name || "Default MySQL"}</span>
              <span className="text-[10px] text-emerald-400/70 font-mono">
                ({activeDbInfo?.tables_count || 11} tables)
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-3 text-xs text-gray-400">
            <div className="flex items-center space-x-1.5 bg-indigo-950/40 text-indigo-300 px-2.5 py-1 rounded-full border border-indigo-800/40">
              <Zap className="w-3 h-3 text-indigo-400" />
              <span>LangGraph Multi-Agent</span>
            </div>
          </div>
        </header>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="max-w-3xl mx-auto py-16 px-6 text-center space-y-8">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-0.5 shadow-2xl shadow-indigo-500/30">
                <div className="w-full h-full bg-[#0B0F19] rounded-[14px] flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-indigo-400" />
                </div>
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-white tracking-tight">
                  Persistent AI Data Analyst
                </h2>
                <p className="text-sm text-gray-400 max-w-lg mx-auto">
                  Ask natural language questions on your business databases, CSVs, Excel files, or SQL dumps.
                  Currently analyzing <strong className="text-indigo-300">{activeDbInfo?.name || "Default MySQL Database"}</strong>.
                </p>
              </div>

              {/* Feature Highlights Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left pt-4">
                <div className="p-4 rounded-xl bg-[#0E1526] border border-[#1F2937]">
                  <Database className="w-5 h-5 text-indigo-400 mb-2" />
                  <h3 className="text-xs font-semibold text-gray-200">Dynamic Introspection</h3>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Auto-discovers tables: {activeDbInfo?.tables?.slice(0, 3).join(", ") || "categories, products, sales"}...
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-[#0E1526] border border-[#1F2937]">
                  <BarChart3 className="w-5 h-5 text-emerald-400 mb-2" />
                  <h3 className="text-xs font-semibold text-gray-200">Automated Visuals</h3>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Generates interactive Plotly charts tailored to your data.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-[#0E1526] border border-[#1F2937]">
                  <TrendingUp className="w-5 h-5 text-amber-400 mb-2" />
                  <h3 className="text-xs font-semibold text-gray-200">Predictive Forecasts</h3>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Projects trends with statsforecast AutoARIMA & confidence intervals.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-[#1F2937]/30 pb-6">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
      </main>

      {/* Upload Database Modal */}
      <DatabaseUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onDatabaseSelected={handleDatabaseSelected}
      />
    </div>
  );
};
