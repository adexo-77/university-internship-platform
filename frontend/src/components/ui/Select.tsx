import React from 'react';
import { cn } from '../../lib/cn';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: SelectOption[];
  helperText?: string;
  error?: string;
}

export const Select: React.FC<SelectProps> = ({
  label,
  options,
  helperText,
  error,
  id,
  className,
  disabled,
  ...props
}) => {
  const generatedId = React.useId();
  const selectId = id ?? generatedId;
  const helperId = `${selectId}-helper`;
  const errorId = `${selectId}-error`;

  return (
    <div className="flex flex-col gap-1.5 w-full">
      <label htmlFor={selectId} className="text-base font-medium text-ink">
        {label}
      </label>
      <select
        id={selectId}
        disabled={disabled}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        className={cn(
          'w-full rounded-control border bg-surface px-3 py-2 text-base text-ink transition-colors duration-150',
          'border-line focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol focus-visible:ring-offset-1 focus-visible:ring-offset-surface',
          'disabled:cursor-not-allowed disabled:bg-chalk disabled:text-pencil',
          error && 'border-brick focus-visible:ring-brick',
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
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
