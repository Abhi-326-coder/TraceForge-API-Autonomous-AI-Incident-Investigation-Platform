import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

export type DataTableColumn<T> = {
  key: string;
  header: string;
  cell: (row: T) => ReactNode;
  className?: string;
};

type DataTableProps<T> = {
  columns: DataTableColumn<T>[];
  rows: T[];
  getRowKey: (row: T, index: number) => string;
  emptyContent?: ReactNode;
};

export function DataTable<T>({ columns, rows, getRowKey, emptyContent }: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-xl border bg-surface">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="bg-surface-subtle text-xs font-medium tracking-wide text-muted uppercase">
          <tr>{columns.map((column) => <th key={column.key} className={cn("px-5 py-3", column.className)}>{column.header}</th>)}</tr>
        </thead>
        <tbody className="divide-y">
          {rows.length ? rows.map((row, index) => (
            <tr key={getRowKey(row, index)} className="text-foreground hover:bg-slate-50/70">
              {columns.map((column) => <td key={column.key} className={cn("px-5 py-4", column.className)}>{column.cell(row)}</td>)}
            </tr>
          )) : (
            <tr><td colSpan={columns.length} className="px-5 py-10">{emptyContent ?? <p className="text-center text-muted">No records found.</p>}</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
