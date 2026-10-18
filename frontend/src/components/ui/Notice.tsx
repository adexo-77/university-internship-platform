import React from 'react';
import { cn } from '../../lib/cn';

export interface NoticeProps {
  variant?: 'info' | 'attention' | 'error';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Notice: React.FC<NoticeProps> = ({ variant = 'info', title, children, className }) => {
  const variantStyles = {
    info: 'bg-petrol-tint border-petrol text-ink',
    attention: 'bg-marigold-tint border-marigold text-ink',
    error: 'bg-surface border-brick text-ink',
  };

  return (
    <div
      role="region"
      aria-label={title ?? 'Notice'}
      className={cn(
        'rounded-control border p-4 text-base leading-normal',
        variantStyles[variant],
        className
      )}
    >
      {title && <h4 className="font-semibold text-ink mb-1">{title}</h4>}
      <div className="text-pencil">{children}</div>
    </div>
  );
};
