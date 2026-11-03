import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { resolveBackTarget } from '../../config/navigation';
import { cn } from '../../lib/cn';

export interface BackLinkProps {
  to?: string;
  label?: string;
  className?: string;
}

/**
 * Standard back navigation control placed at top of content area.
 * Follows browser history when user arrived from within app;
 * otherwise navigates to the canonical parent route.
 */
export const BackLink: React.FC<BackLinkProps> = ({ to, label, className }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const resolved = resolveBackTarget(location.pathname);
  const targetPath = to ?? resolved?.parentPath ?? '/dashboard';
  const targetLabel = label ?? resolved?.label ?? 'Back';

  const handleBack = (): void => {
    if (
      window.history.state &&
      typeof window.history.state.idx === 'number' &&
      window.history.state.idx > 0
    ) {
      navigate(-1);
    } else {
      navigate(targetPath);
    }
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      aria-label={targetLabel}
      data-testid="back-link"
      className={cn(
        'inline-flex items-center gap-1.5 text-xs sm:text-sm font-medium text-pencil hover:text-ink active:text-ink cursor-pointer transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 rounded-control min-h-[44px] py-1 mb-4 select-none',
        className
      )}
    >
      <ArrowLeft className="h-4 w-4 shrink-0 text-current" aria-hidden="true" />
      <span>{targetLabel}</span>
    </button>
  );
};
