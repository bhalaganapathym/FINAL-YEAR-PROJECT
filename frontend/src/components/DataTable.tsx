import React, { useState } from "react";
import { Table, ChevronLeft, ChevronRight } from "lucide-react";

interface DataTableProps {
  columns: string[];
  data: Record<string, any>[];
}

export const DataTable: React.FC<DataTableProps> = ({ columns, data }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 8;

  if (!data || data.length === 0 || !columns || columns.length === 0) {
    return null;
  }

  const totalPages = Math.ceil(data.length / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage;
  const currentRows = data.slice(startIndex, startIndex + rowsPerPage);

  const formatCellValue = (val: any): string => {
    if (val === null || val === undefined) return "-";
    if (typeof val === "number") {
      return Number.isInteger(val) ? val.toLocaleString() : val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return String(val);
  };

  return (
    <div className="my-4 rounded-xl border border-[#1F2937] bg-[#0E1526]/80 backdrop-blur-md overflow-hidden text-xs shadow-xl">
      <div className="px-4 py-2.5 bg-[#111827]/90 border-b border-[#1F2937] flex items-center justify-between">
        <div className="flex items-center space-x-2 font-semibold text-gray-200">
          <Table className="w-4 h-4 text-indigo-400" />
          <span>Result Records</span>
          <span className="px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 text-[10px]">
            {data.length} total
          </span>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center space-x-2 text-gray-400">
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex space-x-1">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="overflow-x-auto max-h-72">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#0B0F19]/90 border-b border-[#1F2937] text-gray-400 font-semibold uppercase tracking-wider text-[10px]">
              {columns.map((col) => (
                <th key={col} className="px-4 py-2.5 whitespace-nowrap">
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1F2937]/50 text-gray-300">
            {currentRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-indigo-950/20 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2 whitespace-nowrap font-mono text-[11px]">
                    {formatCellValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
