import React from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '../ui';
import { AdminDashboardResponse } from '../../types/dashboard';
import { StatStrip } from './StatStrip';

export interface AdminDashboardProps {
  data: AdminDashboardResponse;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ data }) => {
  const totalUsers = Object.values(data.users_by_role).reduce((sum, count) => sum + count, 0);
  const totalCourses = Object.values(data.courses_by_status).reduce((sum, count) => sum + count, 0);
  const totalApplications = Object.values(data.applications_by_status).reduce(
    (sum, count) => sum + count,
    0
  );

  const activeCount = data.users_active_count ?? data.active_users_count ?? 0;
  const pendingReviews = data.postings_pending_review ?? data.internships_pending_review ?? 0;

  const stats = [
    {
      label: 'Users',
      value: totalUsers,
      to: '/admin/users',
      helperText: `${activeCount} active`,
    },
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
      value: pendingReviews,
      to: '/admin/internship-reviews',
      badge:
        pendingReviews > 0 ? (
          <Badge variant="attention">{pendingReviews} pending</Badge>
        ) : undefined,
    },
    {
      label: 'Open internships',
      value: data.open_internships,
      to: '/internships',
    },
  ];

  return (
    <div className="space-y-6">
      <StatStrip items={stats} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Users by Role */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-ink">Users by role</h2>
            <Link to="/admin/users" className="text-xs font-medium text-petrol hover:underline">
              Manage users
            </Link>
          </div>
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {Object.entries(data.users_by_role).map(([role, count]) => (
              <div
                key={role}
                className="p-3 flex items-center justify-between hover:bg-chalk transition-colors"
              >
                <span className="text-sm text-ink capitalize">{role}</span>
                <span className="text-sm font-semibold text-ink tabular-nums">{count}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Courses by Status */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-ink">Courses overview</h2>
            <Link to="/courses" className="text-xs font-medium text-petrol hover:underline">
              Browse catalog ({totalCourses})
            </Link>
          </div>
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {Object.entries(data.courses_by_status).map(([status, count]) => (
              <div
                key={status}
                className="p-3 flex items-center justify-between hover:bg-chalk transition-colors"
              >
                <span className="text-sm text-ink capitalize">{status}</span>
                <span className="text-sm font-semibold text-ink tabular-nums">{count}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Applications by Status */}
        <section className="space-y-3 md:col-span-2">
          <h2 className="text-base font-semibold text-ink">
            Platform applications overview ({totalApplications} total)
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {Object.entries(data.applications_by_status).map(([status, count]) => (
              <div
                key={status}
                className="p-3 bg-surface border border-line rounded-control flex flex-col justify-between"
              >
                <span className="text-xs text-pencil capitalize">{status}</span>
                <span className="text-xl font-semibold text-ink tabular-nums mt-1">{count}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
