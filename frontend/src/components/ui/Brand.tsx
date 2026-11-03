import React from 'react';
import { cn } from '../../lib/cn';

export interface BrandProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  tagline?: string;
}

/**
 * Shared platform brand wordmark and tagline.
 * Uppercase wordmark with modest letter spacing in ink color;
 * tagline in pencil color, wrapping cleanly at 360 px.
 */
export const Brand: React.FC<BrandProps> = ({
  size = 'md',
  className,
  tagline = 'Learning & Internship Platform',
}) => {
  return (
    <div className={cn('flex flex-col', className)} data-testid="platform-brand">
      <span
        className={cn(
          'font-bold uppercase tracking-wider text-ink leading-tight select-none',
          size === 'sm' && 'text-sm sm:text-base',
          size === 'md' && 'text-base sm:text-lg',
          size === 'lg' && 'text-xl sm:text-2xl'
        )}
      >
        UNIVERSITY
      </span>
      {tagline ? (
        <span
          className={cn(
            'text-pencil font-normal leading-tight break-words select-none mt-0.5',
            size === 'sm' && 'text-[11px] sm:text-xs',
            size === 'md' && 'text-xs',
            size === 'lg' && 'text-xs sm:text-sm'
          )}
        >
          {tagline}
        </span>
      ) : null}
    </div>
  );
};
