import React from 'react';
import { cn } from '../../lib/cn';

export interface ProgressBarProps {
  percent: number;
  label?: string;
  showPercent?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percent,
  label,
  showPercent = true,
  className,
}) => {
  const clamped = Math.max(0, Math.min(100, Math.round(percent)));

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div
        className="flex-1 h-2 bg-chalk border border-line rounded-control overflow-hidden"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
      >
        <div
          className="h-full bg-petrol transition-all duration-150"
          style={{ width: `${clamped}%` }}
        />
      </div>
      {showPercent && (
        <span className="text-xs text-pencil tabular-nums font-medium min-w-[36px] text-right">
          {clamped}%
        </span>
      )}
    </div>
  );
};
