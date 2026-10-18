import React from 'react';
import { cn } from '../../lib/cn';

export interface TextFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helperText?: string;
  error?: string;
}

export const TextField: React.FC<TextFieldProps> = ({
  label,
  helperText,
  error,
  id,
  className,
  disabled,
  ...props
}) => {
  const generatedId = React.useId();
  const inputId = id ?? generatedId;
  const helperId = `${inputId}-helper`;
  const errorId = `${inputId}-error`;

  return (
    <div className="flex flex-col gap-1.5 w-full">
      <label htmlFor={inputId} className="text-base font-medium text-ink">
        {label}
      </label>
      <input
        id={inputId}
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
