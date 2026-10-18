import React from 'react';
import { cn } from '../../lib/cn';

export interface ErrorMessageProps {
  whatHappened: string;
  howToFix: string;
  action?: React.ReactNode;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  whatHappened,
  howToFix,
  action,
  className,
}) => {
  return (
    <div
      role="alert"
      className={cn(
        'rounded-control border border-brick bg-surface p-4 text-left transition-colors duration-150',
        className
      )}
    >
      <p className="font-medium text-brick text-base">{whatHappened}</p>
      <p className="mt-1 text-base text-pencil">{howToFix}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
};
