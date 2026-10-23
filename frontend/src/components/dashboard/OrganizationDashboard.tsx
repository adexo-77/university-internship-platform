import React from 'react';
import { Link } from 'react-router-dom';
import { ApplicationStatusBadge } from '../internships/ApplicationStatusBadge';
import { Badge, EmptyState, Notice } from '../ui';
import { ApplicationStatus } from '../../types/application';
import { OrganizationDashboardResponse } from '../../types/dashboard';
import { formatDate } from '../../lib/dates';
import { StatStrip } from './StatStrip';

export interface OrganizationDashboardProps {
  data: OrganizationDashboardResponse;
}

export const OrganizationDashboard: React.FC<OrganizationDashboardProps> = ({ data }) => {
  const postingCounts = data.postings?.counts_by_status ?? data.posting_counts ?? {};
  const totalPostings =
    data.postings?.total ?? Object.values(postingCounts).reduce((sum, count) => sum + count, 0);

  const stats = [
    { label: 'Open postings', value: postingCounts['open'] || 0, to: '/my-internships' },
    { label: 'Total postings', value: totalPostings, to: '/my-internships' },
    {
      label: 'Postings in review',
      value: postingCounts['pending_review'] || 0,
      badge:
        (postingCounts['pending_review'] || 0) > 0 ? (
          <Badge variant="attention">Pending</Badge>
        ) : undefined,
    },
    {
      label: 'Awaiting decision',
      value: data.applications_awaiting_decision,
      badge:
        data.applications_awaiting_decision > 0 ? (
          <Badge variant="attention">Action needed</Badge>
        ) : undefined,
    },
  ];

  return (
    <div className="space-y-6">
      {data.approval_status !== 'approved' && (
        <>
          {data.approval_status === 'rejected' ? (
            <Notice variant="error" title="Organization application rejected">
              {data.approval_note || 'Your organization profile was rejected by an administrator.'}
            </Notice>
          ) : (
            <Notice variant="attention" title="Approval pending">
              Your organization is awaiting admin approval. You can prepare draft postings, but you
              cannot submit them for publication until approved.
            </Notice>
          )}
        </>
      )}

      <StatStrip items={stats} />

      {/* Posting Status Breakdown */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-ink">Postings overview</h2>
          <Link to="/internships/new" className="text-xs font-medium text-petrol hover:underline">
            Create posting
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {(['draft', 'pending_review', 'open', 'closed'] as const).map((status) => (
            <div
              key={status}
              className="p-3 bg-surface border border-line rounded-control flex flex-col justify-between"
            >
              <span className="text-xs text-pencil capitalize">{status.replace('_', ' ')}</span>
              <span className="text-xl font-semibold text-ink tabular-nums mt-1">
                {postingCounts[status] || 0}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Latest Applications Section */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-ink">Latest applications</h2>
          <Link to="/my-internships" className="text-xs font-medium text-petrol hover:underline">
            Manage postings
          </Link>
        </div>
        {data.recent_applications.length === 0 ? (
          <EmptyState
            title="No applications received"
            description="Applications submitted for your internship postings will appear here."
            action={
              <Link
                to="/my-internships"
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
              >
                Manage postings
              </Link>
            }
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.recent_applications.map((app) => (
              <div
                key={app.application_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/applications/${app.application_id}`}
                      className="font-medium text-ink hover:text-petrol transition-colors"
                    >
                      {app.applicant_name}
                    </Link>
                    <ApplicationStatusBadge status={app.status as ApplicationStatus} />
                  </div>
                  <p className="text-xs text-pencil">
                    {app.posting_title} &bull; Applied {formatDate(app.applied_at)}
                  </p>
                </div>
                <div>
                  <Link
                    to={`/applications/${app.application_id}`}
                    className="text-xs font-medium text-petrol hover:underline"
                  >
                    Review &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
