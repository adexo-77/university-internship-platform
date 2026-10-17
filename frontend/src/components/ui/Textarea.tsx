import React from 'react';
import { cn } from '../../lib/utils';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  helperText?: string;
  error?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  helperText,
  error,
  id,
  className,
  disabled,
  rows = 4,
  ...props
}) => {
  const generatedId = React.useId();
  const textareaId = id ?? generatedId;
  const helperId = `${textareaId}-helper`;
  const errorId = `${textareaId}-error`;

  return (
    <div className="flex flex-col gap-1.5 w-full">
      <label htmlFor={textareaId} className="text-base font-medium text-ink">
        {label}
      </label>
      <textarea
        id={textareaId}
        rows={rows}
        disabled={disabled}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        className={cn(
          'w-full rounded-control border bg-surface px-3 py-2 text-base text-ink placeholder:text-pencil transition-colors duration-150',
          'border-line focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 focus-visible:ring-offset-surface',
          'disabled:cursor-not-allowed disabled:bg-chalk disabled:text-pencil',
          error && 'border-brick focus-visible:ring-brick',
          className
        )}
        {...props}
      />
      {error ? (
        <p id={errorId} className="text-xs text-brick">
          {error}
        </p>
      ) : helperText ? (
        <p id={helperId} className="text-xs text-pencil">
          {helperText}
        </p>
      ) : null}
    </div>
  );
};
