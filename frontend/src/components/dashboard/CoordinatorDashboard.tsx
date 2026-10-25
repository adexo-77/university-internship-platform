import React from 'react';
import { Badge } from '../ui';
import { CoordinatorDashboardResponse } from '../../types/dashboard';
import { StatStrip } from './StatStrip';

export interface CoordinatorDashboardProps {
  data: CoordinatorDashboardResponse;
}

export const CoordinatorDashboard: React.FC<CoordinatorDashboardProps> = ({ data }) => {
  const totalApplications = Object.values(data.applications_by_status).reduce(
    (sum, count) => sum + count,
    0
  );

  const stats = [
    {
      label: 'Organizations',
      value: data.organizations_pending_approval,
      to: '/admin/organizations',
      badge:
        data.organizations_pending_approval > 0 ? (
          <Badge variant="attention">{data.organizations_pending_approval} pending</Badge>
        ) : undefined,
    },
    {
      label: 'Internship reviews',
      value: data.internships_pending_review,
      to: '/admin/internship-reviews',
      badge:
        data.internships_pending_review > 0 ? (
          <Badge variant="attention">{data.internships_pending_review} pending</Badge>
        ) : undefined,
    },
    {
      label: 'Open internships',
      value: data.open_internships,
      to: '/internships',
    },
    {
      label: 'Reviews completed',
      value: data.reviews_completed,
      helperText: 'Completed by you',
    },
  ];

  return (
    <div className="space-y-6">
      <StatStrip items={stats} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Review Queues */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-ink">Review work queues</h2>
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            <div className="p-4 flex items-center justify-between hover:bg-chalk transition-colors">
              <div>
                <h3 className="text-sm font-medium text-ink">Organizations</h3>
                <p className="text-xs text-pencil">
                  Review partner registrations and verification requests
                </p>
              </div>
              <a
                href="/admin/organizations"
                className="text-xs font-semibold text-petrol hover:underline"
              >
                View queue ({data.organizations_pending_approval})
              </a>
            </div>
            <div className="p-4 flex items-center justify-between hover:bg-chalk transition-colors">
              <div>
                <h3 className="text-sm font-medium text-ink">Internship postings</h3>
                <p className="text-xs text-pencil">
                  Approve, reject, or request revisions on postings
                </p>
              </div>
              <a
                href="/admin/internship-reviews"
                className="text-xs font-semibold text-petrol hover:underline"
              >
                View queue ({data.internships_pending_review})
              </a>
            </div>
          </div>
        </section>

        {/* Directory Access */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-ink">Platform directory</h2>
          <div className="bg-surface border border-line rounded-control p-4 space-y-2">
            <p className="text-sm text-pencil">
              Access the complete internship catalog to monitor opportunities, inspect application
              deadlines, and view applicant rosters across all postings.
            </p>
            <div className="pt-2">
              <a
                href="/internships"
                className="inline-flex items-center text-xs font-semibold text-petrol hover:underline"
              >
                Browse all postings &rarr;
              </a>
            </div>
          </div>
        </section>

        {/* Applications by Status */}
        <section className="space-y-3 md:col-span-2">
          <h2 className="text-base font-semibold text-ink">
            Platform applications overview ({totalApplications} total)
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {(['submitted', 'shortlisted', 'accepted', 'rejected', 'withdrawn'] as const).map(
              (status) => (
                <div
                  key={status}
                  className="p-3 bg-surface border border-line rounded-control flex flex-col justify-between"
                >
                  <span className="text-xs text-pencil capitalize">{status}</span>
                  <span className="text-xl font-semibold text-ink tabular-nums mt-1">
                    {data.applications_by_status[status] || 0}
                  </span>
                </div>
              )
            )}
          </div>
        </section>
      </div>
    </div>
  );
};
