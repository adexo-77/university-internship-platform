import React, { useMemo } from 'react';
import { TextField } from '../ui/TextField';
import { computeMaxAllowedDeadline } from '../../lib/internship-rules';

export interface InternshipDeadlineFieldProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  status?: string;
  reviewedAt?: string | null;
  required?: boolean;
}

export const InternshipDeadlineField: React.FC<InternshipDeadlineFieldProps> = ({
  value,
  onChange,
  error,
  status,
  reviewedAt,
  required = true,
}) => {
  const { localString, helperText } = useMemo(
    () => computeMaxAllowedDeadline(status, reviewedAt),
    [status, reviewedAt]
  );

  return (
    <TextField
      id="internship-deadline"
      label="Application deadline"
      type="datetime-local"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      error={error}
      max={localString}
      helperText={helperText}
      required={required}
    />
  );
};
