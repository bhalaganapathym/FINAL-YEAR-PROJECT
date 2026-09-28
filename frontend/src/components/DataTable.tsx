import React, { useState } from "react";
import { Table, ChevronLeft, ChevronRight } from "lucide-react";

interface DataTableProps {
  columns: string[];
  data: Record<string, any>[];
  pageSize?: number;
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  pageSize = 6,
}) => {
  const [currentPage, setCurrentPage] = useState(1);

  if (!data || data.length === 0 || !columns || columns.length === 0) {
    return null;
  }

  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const currentData = data.slice(startIndex, startIndex + pageSize);

  const formatValue = (val: any) => {
    if (val === null || val === undefined) return "-";
    if (typeof val === "number") {
      return val.toLocaleString("en-IN", { maximumFractionDigits: 2 });
    }
    return String(val);
  };

  return (
    <div className="border-4 border-black shadow-[8px_8px_0px_0px_#000] bg-white overflow-hidden my-4">
      {/* Table Header Bar */}
      <div className="px-4 py-2.5 bg-[#FFD93D] text-black font-black text-xs uppercase tracking-wider border-b-4 border-black flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Table className="w-4 h-4 stroke-[3px]" />
          <span>QUERY RESULTS ({data.length} TOTAL ROWS)</span>
        </div>
        <span className="px-2 py-0.5 bg-white border-2 border-black font-black text-[10px] shadow-[2px_2px_0px_0px_#000]">
          PAGE {currentPage} OF {totalPages}
        </span>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#C4B5FD] border-b-3 border-black">
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-3.5 py-2.5 text-[11px] font-black uppercase text-black border-r-2 border-black tracking-wider whitespace-nowrap"
                >
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className={`border-b-2 border-black transition-colors ${
                  rowIdx % 2 === 0 ? "bg-white" : "bg-[#FFFDF5]"
                } hover:bg-[#FFD93D]/30`}
              >
                {columns.map((col, colIdx) => (
                  <td
                    key={colIdx}
                    className="px-3.5 py-2.5 text-xs font-bold text-black border-r-2 border-black whitespace-nowrap"
                  >
                    {formatValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="px-4 py-2 bg-[#FFFDF5] border-t-3 border-black flex items-center justify-between text-xs font-bold">
          <span className="text-[11px] uppercase font-bold text-black">
            Showing {startIndex + 1} to {Math.min(startIndex + pageSize, data.length)} of {data.length} records
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="px-2.5 py-1 bg-white hover:bg-[#FF6B6B] hover:text-white disabled:opacity-40 border-2 border-black text-black font-black text-xs uppercase shadow-[2px_2px_0px_0px_#000] flex items-center gap-1 neo-btn"
            >
              <ChevronLeft className="w-3.5 h-3.5 stroke-[3px]" />
              PREV
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-2.5 py-1 bg-white hover:bg-[#FF6B6B] hover:text-white disabled:opacity-40 border-2 border-black text-black font-black text-xs uppercase shadow-[2px_2px_0px_0px_#000] flex items-center gap-1 neo-btn"
            >
              NEXT
              <ChevronRight className="w-3.5 h-3.5 stroke-[3px]" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
