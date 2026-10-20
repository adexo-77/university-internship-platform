import React from 'react';
import { DueBadge } from '../assignments/DueBadge';
import { Internship } from '../../types/internship';

interface InternshipInfoCardProps {
  internship: Internship;
}

export const InternshipInfoCard: React.FC<InternshipInfoCardProps> = ({ internship }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-surface rounded-card border border-line text-sm">
      <div>
        <span className="text-pencil block">Location</span>
        <span className="font-medium text-ink">{internship.location}</span>
      </div>
      <div>
        <span className="text-pencil block">Work mode</span>
        <span className="font-medium text-ink capitalize">{internship.work_mode}</span>
      </div>
      <div>
        <span className="text-pencil block">Duration</span>
        <span className="font-medium text-ink">
          {internship.duration_weeks ? `${internship.duration_weeks} weeks` : 'Flexible'}
        </span>
      </div>
      <div className="md:col-span-3">
        <span className="text-pencil block">Application deadline</span>
        <DueBadge dueAt={internship.application_deadline} />
      </div>
    </div>
  );
};
