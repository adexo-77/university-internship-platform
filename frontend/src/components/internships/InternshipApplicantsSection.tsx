import React from 'react';
import { Application } from '../../types/application';
import { Select } from '../ui/Select';
import { ApplicantsTable } from './ApplicantsTable';

export interface InternshipApplicantsSectionProps {
  postingId?: number;
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
  postingId,
  roster,
  statusFilter,
  onStatusFilterChange,
}) => {
  return (
    <div className="pt-6 border-t border-line space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-ink">Applicants ({roster.length})</h2>
        <div className="flex items-center gap-3">
          <div className="w-48">
            <Select
              id="applicant-status-filter"
              label=""
              value={statusFilter}
              onChange={(e) => onStatusFilterChange(e.target.value)}
              options={STATUS_OPTIONS}
            />
          </div>
          {postingId && (
            <a
              href={`/api/internships/${postingId}/applicants.csv`}
              download={`internship_${postingId}_applicants.csv`}
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs leading-snug bg-surface text-ink border-line hover:bg-chalk shrink-0"
            >
              Export CSV
            </a>
          )}
        </div>
      </div>

      <ApplicantsTable applications={roster} />
    </div>
  );
};
