import React from 'react';
import { cn } from '../../lib/cn';
import { TextField } from '../ui';

interface StudentPreferencesFieldsProps {
  preferredWorkModes: string[];
  onToggleWorkMode: (mode: string) => void;
  preferredLocation: string;
  onLocationChange: (val: string) => void;
  locationError?: string;
  disabled?: boolean;
}

const WORK_MODE_OPTIONS: Array<{ value: string; label: string; description: string }> = [
  { value: 'onsite', label: 'On-site', description: 'Work at company office' },
  { value: 'remote', label: 'Remote', description: 'Work from home anywhere' },
  { value: 'hybrid', label: 'Hybrid', description: 'Mix of office and remote' },
];

export const StudentPreferencesFields: React.FC<StudentPreferencesFieldsProps> = ({
  preferredWorkModes,
  onToggleWorkMode,
  preferredLocation,
  onLocationChange,
  locationError,
  disabled = false,
}) => {
  return (
    <div className="space-y-4 pt-2 border-t border-line">
      <div>
        <label className="block text-sm font-medium text-ink mb-1">Preferred Work Modes</label>
        <p className="text-xs text-pencil mb-2">
          Select all work arrangements you are interested in (optional).
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {WORK_MODE_OPTIONS.map((opt) => {
            const checked = preferredWorkModes.includes(opt.value);
            return (
              <label
                key={opt.value}
                htmlFor={`work-mode-${opt.value}`}
                className={cn(
                  'flex items-start gap-2 p-2.5 rounded-control border text-sm cursor-pointer transition-colors',
                  checked
                    ? 'border-petrol bg-surface ring-1 ring-petrol text-ink font-medium'
                    : 'border-line bg-surface hover:bg-chalk text-pencil'
                )}
              >
                <input
                  id={`work-mode-${opt.value}`}
                  type="checkbox"
                  aria-label={opt.label}
                  value={opt.value}
                  checked={checked}
                  disabled={disabled}
                  onChange={() => onToggleWorkMode(opt.value)}
                  className="mt-0.5 rounded border-line text-petrol focus:ring-petrol accent-petrol"
                />
                <div>
                  <span className="block text-sm text-ink">{opt.label}</span>
                  <span className="block text-xs text-pencil">{opt.description}</span>
                </div>
              </label>
            );
          })}
        </div>
      </div>

      <TextField
        id="student-preferred-location"
        label="Preferred Location"
        type="text"
        value={preferredLocation}
        onChange={(e) => onLocationChange(e.target.value)}
        error={locationError}
        helperText="Target city or region for on-site or hybrid internships (up to 80 characters)."
        disabled={disabled}
      />
    </div>
  );
};
