import React from 'react';
import { Application } from '../../types/application';
import { Select } from '../ui/Select';
import { ApplicantsTable } from './ApplicantsTable';

export interface InternshipApplicantsSectionProps {
  roster: Application[];
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
}

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'withdrawn', label: 'Withdrawn' },
];

export const InternshipApplicantsSection: React.FC<InternshipApplicantsSectionProps> = ({
  roster,
  statusFilter,
  onStatusFilterChange,
}) => {
  return (
    <div className="pt-6 border-t border-line space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-ink">Applicants ({roster.length})</h2>
        <div className="w-48">
          <Select
            id="applicant-status-filter"
            label=""
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            options={STATUS_OPTIONS}
          />
        </div>
      </div>

      <ApplicantsTable applications={roster} />
    </div>
  );
};
