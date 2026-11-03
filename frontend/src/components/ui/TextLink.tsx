import React from 'react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/cn';

export interface TextLinkProps {
  to?: string;
  href?: string;
  variant?: 'primary' | 'subtle' | 'danger';
  className?: string;
  children: React.ReactNode;
  target?: string;
  rel?: string;
  onClick?: (e: React.MouseEvent) => void;
  title?: string;
}

export const TextLink: React.FC<TextLinkProps> = ({
  to,
  href,
  variant = 'primary',
  className,
  children,
  target,
  rel,
  onClick,
  title,
}) => {
  const baseStyles =
    'inline-flex items-center font-medium underline underline-offset-2 transition-colors duration-150 cursor-pointer min-h-[44px] sm:min-h-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 rounded-sm';

  const variantStyles = {
    primary: 'text-petrol hover:text-petrol-hover active:text-ink',
    subtle: 'text-pencil hover:text-ink active:text-ink',
    danger: 'text-brick hover:text-brick/80 active:text-ink',
  };

  const combinedClasses = cn(baseStyles, variantStyles[variant], className);

  if (to) {
    return (
      <Link to={to} className={combinedClasses} onClick={onClick} title={title}>
        {children}
      </Link>
    );
  }

  return (
    <a
      href={href ?? '#'}
      target={target}
      rel={target === '_blank' ? (rel ?? 'noopener noreferrer') : rel}
      className={combinedClasses}
      onClick={onClick}
      title={title}
    >
      {children}
    </a>
  );
};
