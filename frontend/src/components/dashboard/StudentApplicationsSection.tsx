import React from 'react';
import { Link } from 'react-router-dom';
import { ApplicationStatusBadge } from '../internships/ApplicationStatusBadge';
import { EmptyState } from '../ui';
import { ApplicationStatus } from '../../types/application';
import { StudentApplicationsSummary } from '../../types/dashboard';
import { formatDate } from '../../lib/dates';

export interface StudentApplicationsSectionProps {
  applications: StudentApplicationsSummary;
  totalApplications: number;
}

export const StudentApplicationsSection: React.FC<StudentApplicationsSectionProps> = ({
  applications,
  totalApplications,
}) => {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-ink">Internship applications</h2>
        {totalApplications > 0 && (
          <Link to="/my-applications" className="text-xs font-medium text-petrol hover:underline">
            View all
          </Link>
        )}
      </div>
      {applications.recent.length === 0 ? (
        <EmptyState
          title="No applications submitted"
          description="Explore open internship postings to submit an application."
          action={
            <Link
              to="/internships"
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
            >
              Browse internships
            </Link>
          }
        />
      ) : (
        <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
          {applications.recent.map((app) => (
            <div
              key={app.id}
              className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
            >
              <div className="space-y-0.5">
                <Link
                  to={`/applications/${app.id}`}
                  className="font-medium text-ink hover:text-petrol transition-colors"
                >
                  {app.posting_title}
                </Link>
                <p className="text-xs text-pencil">
                  {app.organization_name} &bull; Applied {formatDate(app.applied_at)}
                </p>
              </div>
              <div>
                <ApplicationStatusBadge status={app.status as ApplicationStatus} />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
