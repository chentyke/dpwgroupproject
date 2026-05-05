import type { KeyboardEvent, ReactNode } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

type Column<T> = {
  key: string;
  label: string;
  render: (row: T) => ReactNode;
};

type RowKey = string | number;

type DataTableProps<T> = {
  columns: Array<Column<T>>;
  rows: T[];
  getRowKey?: (row: T, index: number) => RowKey;
  onRowClick?: (row: T, index: number) => void;
  selectedRowKey?: RowKey | null;
  rowAriaLabel?: (row: T, index: number) => string;
};

export function DataTable<T>({
  columns,
  rows,
  getRowKey,
  onRowClick,
  selectedRowKey,
  rowAriaLabel,
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted p-5 text-sm text-muted-foreground">
        No rows available for the current filter.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-background">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/80">
              {columns.map((column) => (
                <TableHead
                  key={column.key}
                  className="whitespace-nowrap text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground"
                >
                  {column.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, index) => {
              const rowKey = getRowKey?.(row, index) ?? index;
              const isInteractive = Boolean(onRowClick);
              const isSelected = selectedRowKey === rowKey;

              return (
                <TableRow
                  key={rowKey}
                  aria-label={rowAriaLabel?.(row, index)}
                  aria-selected={isInteractive ? isSelected : undefined}
                  className={cn(
                    "align-top",
                    isInteractive &&
                      "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  )}
                  data-state={isSelected ? "selected" : undefined}
                  tabIndex={isInteractive ? 0 : undefined}
                  {...(isInteractive
                    ? {
                        onClick: () => onRowClick?.(row, index),
                        onKeyDown: (event: KeyboardEvent<HTMLTableRowElement>) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            onRowClick?.(row, index);
                          }
                        },
                      }
                    : {})}
                >
                  {columns.map((column) => (
                    <TableCell key={column.key} className="text-foreground">
                      {column.render(row)}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
