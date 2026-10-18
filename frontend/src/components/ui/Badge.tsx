import React from 'react';
import { cn } from '../../lib/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'attention' | 'error' | 'neutral';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  className,
  children,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-badge border leading-normal';

  const variantStyles = {
    success: 'bg-surface text-moss border-moss',
    attention: 'bg-marigold-tint text-ink border-marigold',
    error: 'bg-surface text-brick border-brick',
    neutral: 'bg-chalk text-pencil border-line',
  };

  return (
    <span className={cn(baseStyles, variantStyles[variant], className)} {...props}>
      {children}
    </span>
  );
};
