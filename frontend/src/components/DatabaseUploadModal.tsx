import React, { useState, useRef } from "react";
import { Upload, Link2, X, FileText, CheckCircle2, AlertCircle, Loader2, Database, Sparkles } from "lucide-react";
import { api } from "../services/api";
import { DatabaseSourceInfo } from "../types";

interface DatabaseUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDatabaseSelected: (db: DatabaseSourceInfo) => void;
}

export const DatabaseUploadModal: React.FC<DatabaseUploadModalProps> = ({
  isOpen,
  onClose,
  onDatabaseSelected,
}) => {
  const [tab, setTab] = useState<"file" | "uri">("file");
  const [file, setFile] = useState<File | null>(null);
  const [uri, setUri] = useState("");
  const [connectionName, setConnectionName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successInfo, setSuccessInfo] = useState<DatabaseSourceInfo | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const res = await api.uploadDatabase(file);
      setSuccessInfo(res);
      onDatabaseSelected(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Failed to upload file.");
    } finally {
      setLoading(false);
    }
  };

  const handleConnectUri = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uri.trim()) {
      setError("Please provide a database connection URI.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const res = await api.connectDatabaseUri(uri.trim(), connectionName.trim() || undefined);
      setSuccessInfo(res);
      onDatabaseSelected(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Failed to connect to database URI.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-[#FFFDF5] border-6 border-black shadow-[16px_16px_0px_0px_#000] flex flex-col relative">
        {/* Header */}
        <div className="px-6 py-4 bg-[#FFD93D] border-b-4 border-black flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000] flex items-center justify-center">
              <Database className="w-5 h-5 stroke-[3px] text-black" />
            </div>
            <div>
              <h3 className="text-sm font-black uppercase text-black">CONNECT DATASET / DATABASE</h3>
              <p className="text-[10px] font-bold text-black uppercase">SQLite, CSV, Excel or Remote URI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 bg-white hover:bg-[#FF6B6B] hover:text-white border-2 border-black shadow-[2px_2px_0px_0px_#000] neo-btn"
          >
            <X className="w-4 h-4 stroke-[3px]" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b-4 border-black bg-white">
          <button
            onClick={() => { setTab("file"); setError(null); }}
            className={`flex-1 py-3 px-4 text-xs font-black uppercase tracking-wider flex items-center justify-center space-x-2 border-r-4 border-black transition-colors ${
              tab === "file"
                ? "bg-[#C4B5FD] text-black"
                : "bg-white text-black hover:bg-[#FFFDF5]"
            }`}
          >
            <Upload className="w-4 h-4 stroke-[3px]" />
            <span>Upload File (.db, .csv, .xlsx, .sql)</span>
          </button>
          <button
            onClick={() => { setTab("uri"); setError(null); }}
            className={`flex-1 py-3 px-4 text-xs font-black uppercase tracking-wider flex items-center justify-center space-x-2 transition-colors ${
              tab === "uri"
                ? "bg-[#C4B5FD] text-black"
                : "bg-white text-black hover:bg-[#FFFDF5]"
            }`}
          >
            <Link2 className="w-4 h-4 stroke-[3px]" />
            <span>Remote URI</span>
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 bg-[#FF6B6B] border-3 border-black shadow-[3px_3px_0px_0px_#000] text-white text-xs font-black uppercase flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 stroke-[3px]" />
              <span>{error}</span>
            </div>
          )}

          {successInfo ? (
            <div className="p-5 bg-[#10B981] border-4 border-black shadow-[6px_6px_0px_0px_#000] text-white text-xs space-y-3">
              <div className="flex items-center space-x-2 font-black uppercase">
                <CheckCircle2 className="w-5 h-5 stroke-[3px]" />
                <span className="text-sm">Database Ingested & Mounted!</span>
              </div>
              <div className="bg-white text-black p-3 border-3 border-black space-y-1 font-bold">
                <div><strong>NAME:</strong> {successInfo.name}</div>
                <div><strong>TYPE:</strong> {successInfo.source_type.toUpperCase()}</div>
                <div><strong>TABLES ({successInfo.tables_count}):</strong> {successInfo.tables.join(", ")}</div>
              </div>
              <div className="pt-2">
                <button
                  onClick={onClose}
                  className="w-full py-3 bg-[#FFD93D] hover:bg-[#ffe053] text-black border-3 border-black shadow-[3px_3px_0px_0px_#000] font-black uppercase text-xs flex items-center justify-center space-x-1.5 neo-btn"
                >
                  <Sparkles className="w-4 h-4 stroke-[3px]" />
                  <span>START ASKING QUESTIONS</span>
                </button>
              </div>
            </div>
          ) : (
            <>
              {tab === "file" ? (
                <div className="space-y-4">
                  {/* Dropzone */}
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleFileDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-4 border-dashed border-black bg-white hover:bg-[#FFD93D]/20 p-8 text-center cursor-pointer shadow-[4px_4px_0px_0px_#000] transition-colors"
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".db,.sqlite,.sqlite3,.csv,.xlsx,.xls,.sql"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <div className="w-12 h-12 bg-[#FFD93D] border-3 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center text-black mx-auto mb-3 rotate-[-2deg]">
                      <FileText className="w-6 h-6 stroke-[3px]" />
                    </div>
                    <p className="text-xs font-black uppercase text-black">
                      {file ? file.name : "CLICK OR DRAG & DROP DATASET FILE HERE"}
                    </p>
                    <p className="text-[10px] font-bold text-gray-600 mt-1 uppercase">
                      Supports SQLite (.db), CSV (.csv), Excel (.xlsx), and SQL Dumps (.sql) up to 50MB
                    </p>
                  </div>

                  <button
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="w-full py-3.5 bg-[#FF6B6B] hover:bg-[#ff5252] disabled:opacity-40 text-white font-black text-xs uppercase tracking-wider border-4 border-black shadow-[4px_4px_0px_0px_#000] flex items-center justify-center space-x-2 neo-btn"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin stroke-[3px]" />
                        <span>PARSING & INGESTING DATASET...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 stroke-[3px]" />
                        <span>UPLOAD & MOUNT DATASET</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <form onSubmit={handleConnectUri} className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-black uppercase text-black mb-1">
                      Display Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={connectionName}
                      onChange={(e) => setConnectionName(e.target.value)}
                      placeholder="e.g. Production Analytics DB"
                      className="w-full px-3 py-2 bg-white border-3 border-black text-xs font-bold text-black focus:bg-[#FFD93D] focus:outline-none shadow-[2px_2px_0px_0px_#000]"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-black uppercase text-black mb-1">
                      Database Connection URI *
                    </label>
                    <input
                      type="text"
                      value={uri}
                      onChange={(e) => setUri(e.target.value)}
                      placeholder="mysql+pymysql://user:password@localhost:3306/dbname"
                      className="w-full px-3 py-2 bg-white border-3 border-black text-xs font-bold text-black focus:bg-[#FFD93D] focus:outline-none font-mono shadow-[2px_2px_0px_0px_#000]"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={!uri.trim() || loading}
                    className="w-full py-3.5 bg-[#FF6B6B] hover:bg-[#ff5252] disabled:opacity-40 text-white font-black text-xs uppercase tracking-wider border-4 border-black shadow-[4px_4px_0px_0px_#000] flex items-center justify-center space-x-2 neo-btn mt-3"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin stroke-[3px]" />
                        <span>CONNECTING & REFLECTING SCHEMA...</span>
                      </>
                    ) : (
                      <>
                        <Link2 className="w-4 h-4 stroke-[3px]" />
                        <span>CONNECT & INTROSPECT SCHEMA</span>
                      </>
                    )}
                  </button>
                </form>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
