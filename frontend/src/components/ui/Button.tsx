import React from 'react';
import { cn } from '../../lib/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'quiet' | 'danger';
  size?: 'sm' | 'md';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  disabled,
  type = 'button',
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 focus-visible:ring-offset-surface disabled:cursor-not-allowed disabled:bg-chalk disabled:text-pencil disabled:border-line disabled:hover:bg-chalk disabled:hover:text-pencil disabled:hover:border-line';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-base leading-snug',
  };

  const variantStyles = {
    primary:
      'bg-petrol text-surface border-petrol hover:bg-petrol-hover hover:border-petrol-hover active:bg-petrol-hover',
    secondary: 'bg-surface text-ink border-line hover:bg-chalk active:bg-line',
    quiet: 'bg-transparent text-pencil border-transparent hover:text-ink hover:bg-chalk',
    danger: 'bg-surface text-brick border-brick hover:bg-chalk active:bg-line',
  };

  return (
    <button
      type={type}
      disabled={disabled}
      className={cn(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      {...props}
    >
      {children}
    </button>
  );
};
