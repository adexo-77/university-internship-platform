import React from 'react';
import { cn } from '../../lib/cn';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  'aria-label': string;
  icon: React.ReactNode;
  variant?: 'secondary' | 'ghost' | 'quiet';
  size?: 'sm' | 'md';
}

export const IconButton: React.FC<IconButtonProps> = ({
  'aria-label': ariaLabel,
  icon,
  variant = 'secondary',
  size = 'md',
  className,
  disabled,
  type = 'button',
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center rounded-control transition-colors duration-150 cursor-pointer min-h-[44px] min-w-[44px] sm:min-h-0 sm:min-w-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 focus-visible:ring-offset-surface disabled:cursor-not-allowed disabled:bg-chalk disabled:text-pencil disabled:border-line active:scale-95';

  const sizeStyles = {
    sm: 'p-1.5 text-xs h-11 w-11 sm:h-8 sm:w-8',
    md: 'p-2 text-base h-11 w-11 sm:h-10 sm:w-10',
  };

  const variantStyles = {
    secondary:
      'bg-surface text-pencil hover:text-ink border border-line hover:bg-chalk active:bg-line',
    ghost:
      'bg-transparent text-pencil hover:text-ink border border-transparent hover:bg-chalk active:bg-line',
    quiet:
      'bg-transparent text-pencil hover:text-ink border border-transparent hover:bg-chalk active:bg-line',
  };

  return (
    <button
      type={type}
      aria-label={ariaLabel}
      disabled={disabled}
      className={cn(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      {...props}
    >
      {icon}
    </button>
  );
};
