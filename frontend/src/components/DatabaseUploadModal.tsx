import React, { useState, useRef } from "react";
import { Upload, Link2, X, FileText, CheckCircle2, AlertCircle, Loader2, Database } from "lucide-react";
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div className="w-full max-w-lg rounded-2xl bg-[#0E1526] border border-[#1F2937] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#1F2937] flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Connect Your Database / Dataset</h3>
              <p className="text-[11px] text-gray-400">Upload SQLite, CSV, Excel or connect remote database</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-[#1F2937] bg-[#070B14]/60 px-6 pt-2">
          <button
            onClick={() => { setTab("file"); setError(null); }}
            className={`pb-2.5 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all ${
              tab === "file"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload File (.db, .csv, .xlsx, .sql)</span>
          </button>
          <button
            onClick={() => { setTab("uri"); setError(null); }}
            className={`pb-2.5 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all ${
              tab === "uri"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <Link2 className="w-3.5 h-3.5" />
            <span>Remote URI</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-rose-950/50 border border-rose-800/50 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {successInfo ? (
            <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/40 text-xs space-y-3">
              <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Successfully Mounted Database!</span>
              </div>
              <div className="text-gray-300 text-[11px] space-y-1">
                <div><strong className="text-gray-400">Source:</strong> {successInfo.name}</div>
                <div><strong className="text-gray-400">Type:</strong> {successInfo.source_type.toUpperCase()}</div>
                <div><strong className="text-gray-400">Tables Created ({successInfo.tables_count}):</strong> {successInfo.tables.join(", ")}</div>
              </div>
              <div className="pt-2">
                <button
                  onClick={onClose}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-xs transition-colors"
                >
                  Start Asking Questions
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
                    className="border-2 border-dashed border-[#1F2937] hover:border-indigo-500/60 rounded-xl p-6 text-center cursor-pointer bg-[#070B14]/40 hover:bg-[#070B14]/80 transition-all"
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".db,.sqlite,.sqlite3,.csv,.xlsx,.xls,.sql"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <FileText className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                    <p className="text-xs font-semibold text-gray-200">
                      {file ? file.name : "Click or Drag & Drop database file here"}
                    </p>
                    <p className="text-[11px] text-gray-500 mt-1">
                      Supports SQLite (.db), CSV (.csv), Excel (.xlsx), and SQL Dumps (.sql) up to 50MB
                    </p>
                  </div>

                  <button
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-medium text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-indigo-600/30"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Parsing & Mounting Database...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        <span>Upload & Analyze Dataset</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <form onSubmit={handleConnectUri} className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-gray-400 mb-1">
                      Display Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={connectionName}
                      onChange={(e) => setConnectionName(e.target.value)}
                      placeholder="e.g. Production Analytics DB"
                      className="w-full px-3 py-2 bg-[#070B14] border border-[#1F2937] focus:border-indigo-500 rounded-lg text-xs text-gray-200 placeholder-gray-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-gray-400 mb-1">
                      Database Connection URI *
                    </label>
                    <input
                      type="text"
                      value={uri}
                      onChange={(e) => setUri(e.target.value)}
                      placeholder="mysql+pymysql://user:password@localhost:3306/dbname"
                      className="w-full px-3 py-2 bg-[#070B14] border border-[#1F2937] focus:border-indigo-500 rounded-lg text-xs text-gray-200 placeholder-gray-500 focus:outline-none font-mono text-[11px]"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={!uri.trim() || loading}
                    className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-medium text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-indigo-600/30 mt-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Connecting & Reflecting Schema...</span>
                      </>
                    ) : (
                      <>
                        <Link2 className="w-4 h-4" />
                        <span>Connect & Introspect Schema</span>
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
