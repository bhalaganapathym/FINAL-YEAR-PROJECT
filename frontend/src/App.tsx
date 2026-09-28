import React, { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { api } from "./services/api";
import { MessageItem, ConversationSummary, QueryResponse, DatabaseSourceInfo } from "./types";
import { Sidebar } from "./components/Sidebar";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { DatabaseUploadModal } from "./components/DatabaseUploadModal";
import { Sparkles, Database, BarChart3, TrendingUp, Zap, HardDrive, ArrowUpRight } from "lucide-react";

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
    <div className="flex h-screen bg-[#FFFDF5] text-black overflow-hidden font-sans">
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

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Navbar */}
        <header className="h-14 border-b-4 border-black bg-[#FFD93D] px-6 flex items-center justify-between z-10">
          <div className="flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-2 bg-white text-black px-3.5 py-1.5 border-3 border-black font-black uppercase shadow-[3px_3px_0px_0px_#000]">
              <HardDrive className="w-4 h-4 stroke-[3px]" />
              <span>TARGET DB: {activeDbInfo?.name || "Default MySQL"}</span>
              <span className="px-1.5 py-0.2 bg-[#FF6B6B] text-white border border-black font-mono text-[10px]">
                {activeDbInfo?.tables_count || 11} TABLES
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-1.5 bg-[#FF6B6B] text-white px-3 py-1.5 border-3 border-black font-black uppercase shadow-[3px_3px_0px_0px_#000] rotate-[1deg]">
              <Zap className="w-4 h-4 stroke-[3px]" />
              <span>LANGGRAPH MULTI-AGENT</span>
            </div>
          </div>
        </header>

        {/* Message Stream or Empty State Hero */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="max-w-4xl mx-auto py-12 px-6 space-y-10">
              {/* Hero Banner */}
              <div className="text-center space-y-4">
                <div className="inline-block p-4 bg-[#FFD93D] border-4 border-black shadow-[6px_6px_0px_0px_#000] rotate-[-2deg] mb-2">
                  <Sparkles className="w-10 h-10 stroke-[3px] text-black mx-auto" />
                </div>

                <h1 className="text-4xl sm:text-5xl font-black uppercase text-black tracking-tight leading-none">
                  PERSISTENT AI <br />
                  <span className="bg-[#FF6B6B] text-white px-3 py-1 border-4 border-black inline-block mt-2 rotate-[1deg] shadow-[5px_5px_0px_0px_#000]">
                    DATA ANALYST
                  </span>
                </h1>

                <p className="text-sm font-bold text-black max-w-xl mx-auto uppercase tracking-wide pt-2">
                  CONVERSATIONAL BUSINESS INTELLIGENCE POWERED BY LANGGRAPH & STATSFORECAST.
                  ANALYZING <span className="bg-[#C4B5FD] px-1.5 py-0.5 border-2 border-black">{activeDbInfo?.name || "DEFAULT MYSQL DATABASE"}</span>.
                </p>
              </div>

              {/* Bento Feature Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
                <div className="p-5 bg-white border-4 border-black shadow-[8px_8px_0px_0px_#000] neo-card">
                  <div className="w-10 h-10 bg-[#FFD93D] border-3 border-black flex items-center justify-center mb-3">
                    <Database className="w-5 h-5 stroke-[3px] text-black" />
                  </div>
                  <h3 className="text-xs font-black uppercase text-black mb-1">
                    DYNAMIC INTROSPECTION
                  </h3>
                  <p className="text-[11px] font-bold text-gray-700 leading-relaxed uppercase">
                    Zero hardcoded schemas. Auto-discovers tables: {activeDbInfo?.tables?.slice(0, 3).join(", ") || "categories, products, sales"}...
                  </p>
                </div>

                <div className="p-5 bg-white border-4 border-black shadow-[8px_8px_0px_0px_#000] neo-card">
                  <div className="w-10 h-10 bg-[#FF6B6B] border-3 border-black flex items-center justify-center mb-3 text-white">
                    <BarChart3 className="w-5 h-5 stroke-[3px]" />
                  </div>
                  <h3 className="text-xs font-black uppercase text-black mb-1">
                    ADAPTIVE PLOTLY CHARTS
                  </h3>
                  <p className="text-[11px] font-bold text-gray-700 leading-relaxed uppercase">
                    Generates interactive Bar, Line, Pie/Donut, Area, and KPI graphs tailored to your prompt.
                  </p>
                </div>

                <div className="p-5 bg-white border-4 border-black shadow-[8px_8px_0px_0px_#000] neo-card">
                  <div className="w-10 h-10 bg-[#10B981] border-3 border-black flex items-center justify-center mb-3 text-white">
                    <TrendingUp className="w-5 h-5 stroke-[3px]" />
                  </div>
                  <h3 className="text-xs font-black uppercase text-black mb-1">
                    PREDICTIVE FORECASTING
                  </h3>
                  <p className="text-[11px] font-bold text-gray-700 leading-relaxed uppercase">
                    Trained on historical data using statsforecast AutoARIMA with 80% & 95% confidence intervals.
                  </p>
                </div>
              </div>

              {/* Starter Prompts Box */}
              <div className="p-5 bg-[#C4B5FD] border-4 border-black shadow-[8px_8px_0px_0px_#000] space-y-3">
                <div className="text-xs font-black uppercase text-black flex items-center gap-2">
                  <Sparkles className="w-4 h-4 stroke-[3px]" />
                  <span>CLICK A STARTER QUERY TO BEGIN:</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {[
                    "Show total sales and profit by region for 2024",
                    "Which 5 products generated the highest revenue?",
                    "Show brand count as a pie chart",
                    "Forecast monthly sales for the next 6 months",
                  ].map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="p-3 text-left bg-white hover:bg-[#FFD93D] border-3 border-black shadow-[3px_3px_0px_0px_#000] text-xs font-black uppercase flex items-center justify-between transition-all neo-btn group"
                    >
                      <span className="truncate pr-2">{prompt}</span>
                      <ArrowUpRight className="w-4 h-4 stroke-[3px] shrink-0 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y-4 divide-black/20 pb-8">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Input Form */}
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
      </main>

      {/* Database Upload Modal */}
      <DatabaseUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onDatabaseSelected={handleDatabaseSelected}
      />
    </div>
  );
};
