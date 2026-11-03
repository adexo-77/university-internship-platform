import React from 'react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/cn';

export interface CardProps {
  to?: string;
  href?: string;
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
  interactive?: boolean;
}

export const Card: React.FC<CardProps> = ({
  to,
  href,
  onClick,
  className,
  children,
  interactive,
}) => {
  const isClickable = Boolean(to || href || onClick || interactive);

  const baseStyles = 'bg-surface border border-line rounded-control p-4 text-ink block';
  const interactiveStyles =
    'cursor-pointer transition-all duration-150 hover:border-petrol hover:bg-chalk/40 active:bg-line/20 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 min-h-[44px]';

  const combinedClasses = cn(baseStyles, isClickable && interactiveStyles, className);

  if (to) {
    return (
      <Link to={to} onClick={onClick} className={combinedClasses}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} onClick={onClick} className={combinedClasses}>
        {children}
      </a>
    );
  }

  if (onClick) {
    return (
      <div
        role="button"
        tabIndex={0}
        onClick={onClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick();
          }
        }}
        className={combinedClasses}
      >
        {children}
      </div>
    );
  }

  return <div className={combinedClasses}>{children}</div>;
};
