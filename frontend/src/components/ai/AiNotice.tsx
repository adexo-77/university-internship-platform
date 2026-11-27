import React from 'react';
import { cn } from '../../lib/cn';

export interface AiNoticeProps {
  className?: string;
  children?: React.ReactNode;
}

const DEFAULT_TEXT = 'AI-generated draft. Check it before use.';

export const AiNotice: React.FC<AiNoticeProps> = ({ className, children }) => {
  return (
    <p
      className={cn(
        'inline-flex items-center gap-1 rounded-control bg-marigold-tint border border-marigold px-2 py-1 text-xs text-ink',
        className
      )}
    >
      <span aria-hidden="true">✦</span>
      <span>{children ?? DEFAULT_TEXT}</span>
    </p>
  );
};
