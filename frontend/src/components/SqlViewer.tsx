import React, { useState } from "react";
import { ChevronDown, ChevronRight, Copy, Check, Terminal } from "lucide-react";

interface SqlViewerProps {
  sql: string;
  executionTimeMs?: number;
  rowCount?: number;
}

export const SqlViewer: React.FC<SqlViewerProps> = ({
  sql,
  executionTimeMs,
  rowCount,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-xl border border-[#1F2937] bg-[#0A0E17]/90 overflow-hidden text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2.5 flex items-center justify-between bg-[#111827]/80 hover:bg-[#1E293B]/60 transition-colors text-gray-300 select-none"
      >
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-indigo-400" />
          <span className="font-semibold text-gray-200">Generated MySQL Query</span>
          {rowCount !== undefined && (
            <span className="px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 text-[10px]">
              {rowCount} rows
            </span>
          )}
          {executionTimeMs !== undefined && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 text-[10px] border border-emerald-800/40">
              ⚡ {executionTimeMs}ms
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title="Copy SQL"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          {isOpen ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 bg-[#050811] border-t border-[#1F2937] overflow-x-auto">
          <pre className="font-mono text-[12px] leading-relaxed text-indigo-200 whitespace-pre">
            {sql}
          </pre>
        </div>
      )}
    </div>
  );
};
