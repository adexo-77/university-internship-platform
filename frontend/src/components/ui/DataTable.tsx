import React from 'react';
import { cn } from '../../lib/utils';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  isNumeric?: boolean;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  className?: string;
  emptyMessage?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  className,
  emptyMessage = 'No records to display',
}: DataTableProps<T>) {
  return (
    <div
      className={cn(
        'w-full overflow-x-auto rounded-control border border-line bg-surface',
        className
      )}
    >
      <table className="w-full border-collapse text-left text-base">
        <thead>
          <tr className="border-b border-line bg-chalk">
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={cn(
                  'px-4 py-3 font-medium text-pencil text-xs',
                  column.isNumeric ? 'text-right tabular-nums' : 'text-left'
                )}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-pencil text-base">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr
                key={keyExtractor(item)}
                className="transition-colors duration-150 hover:bg-chalk/50"
              >
                {columns.map((column) => {
                  const content = column.render
                    ? column.render(item)
                    : (item as Record<string, unknown>)[column.key];

                  return (
                    <td
                      key={column.key}
                      className={cn(
                        'px-4 py-3.5 text-ink text-base',
                        column.isNumeric ? 'text-right tabular-nums' : 'text-left'
                      )}
                    >
                      {content as React.ReactNode}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
