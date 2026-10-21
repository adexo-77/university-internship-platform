import React from 'react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/cn';

export interface StatItem {
  label: string;
  value: React.ReactNode;
  badge?: React.ReactNode;
  to?: string;
  helperText?: string;
}

export interface StatStripProps {
  items: StatItem[];
  className?: string;
}

export const StatStrip: React.FC<StatStripProps> = ({ items, className }) => {
  return (
    <div
      className={cn(
        'grid grid-cols-2 md:grid-flow-col md:auto-cols-fr bg-surface border border-line rounded-control divide-y md:divide-y-0 md:divide-x divide-line',
        className
      )}
    >
      {items.map((item, index) => {
        const content = (
          <>
            <span className="text-xs text-pencil font-medium">{item.label}</span>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <span className="text-2xl font-semibold text-ink tabular-nums">{item.value}</span>
              {item.badge}
            </div>
            {item.helperText && <span className="text-xs text-pencil mt-1">{item.helperText}</span>}
          </>
        );

        if (item.to) {
          return (
            <Link
              key={index}
              to={item.to}
              className="p-4 flex flex-col justify-between hover:bg-chalk transition-colors group"
            >
              {content}
            </Link>
          );
        }

        return (
          <div key={index} className="p-4 flex flex-col justify-between">
            {content}
          </div>
        );
      })}
    </div>
  );
};
