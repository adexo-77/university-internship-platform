import React from 'react';
import { cn } from '../../lib/cn';

export interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-control border border-line bg-surface p-8 text-center',
        className
      )}
    >
      <h3 className="text-base font-semibold text-ink">{title}</h3>
      <p className="mt-1.5 max-w-[60ch] text-base text-pencil">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};
