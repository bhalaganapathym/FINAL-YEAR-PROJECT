import React, { useState } from "react";
import { Terminal, Copy, Check, ChevronDown, ChevronRight, Zap } from "lucide-react";

interface SqlViewerProps {
  sql?: string;
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

  if (!sql) return null;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border-4 border-black shadow-[6px_6px_0px_0px_#000] bg-white overflow-hidden my-3">
      {/* Header Accordion */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-[#FFD93D] hover:bg-[#ffe053] flex items-center justify-between text-black font-black text-xs uppercase tracking-wide border-b-4 border-black transition-colors"
      >
        <div className="flex items-center space-x-2">
          {isOpen ? (
            <ChevronDown className="w-4 h-4 stroke-[3px]" />
          ) : (
            <ChevronRight className="w-4 h-4 stroke-[3px]" />
          )}
          <Terminal className="w-4 h-4 stroke-[3px]" />
          <span>GENERATED SQL QUERY</span>
        </div>

        <div className="flex items-center space-x-2">
          {rowCount !== undefined && (
            <span className="px-2 py-0.5 bg-white border-2 border-black text-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000]">
              {rowCount} ROWS
            </span>
          )}
          {executionTimeMs !== undefined && (
            <span className="px-2 py-0.5 bg-[#C4B5FD] border-2 border-black text-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000] flex items-center gap-1">
              <Zap className="w-3 h-3 stroke-[3px]" />
              {executionTimeMs.toFixed(1)} MS
            </span>
          )}
          <div
            onClick={handleCopy}
            className="p-1.5 bg-white hover:bg-[#FF6B6B] hover:text-white border-2 border-black shadow-[2px_2px_0px_0px_#000] transition-colors cursor-pointer"
            title="Copy SQL"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 stroke-[3px]" />
            ) : (
              <Copy className="w-3.5 h-3.5 stroke-[3px]" />
            )}
          </div>
        </div>
      </button>

      {/* Collapsible Code Block */}
      {isOpen && (
        <div className="p-4 bg-black overflow-x-auto text-[#00FF66] font-mono text-xs leading-relaxed font-bold border-t-0">
          <pre className="whitespace-pre-wrap">{sql}</pre>
        </div>
      )}
    </div>
  );
};
