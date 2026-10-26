import React from 'react';
import { Download, FileSpreadsheet, Users } from 'lucide-react';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';

export const ReportsPage: React.FC = () => {
  usePageTitle('Reports');
  const { user } = useAuth();

  const isAdmin = user?.role === 'admin';
  const isCoordinator = user?.role === 'coordinator';

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Reports"
          description="Generate and export platform datasets as safe UTF-8 CSV spreadsheets."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Applications Report: Admin & Coordinator */}
          {(isAdmin || isCoordinator) && (
            <div
              data-testid="applications-report-card"
              className="p-6 bg-surface border border-line rounded-control flex flex-col justify-between space-y-4 shadow-none"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-chalk text-petrol flex items-center justify-center">
                    <FileSpreadsheet className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-ink">Internship applications</h3>
                    <p className="text-xs text-pencil">Comprehensive candidate pipeline dataset</p>
                  </div>
                </div>
                <p className="text-sm text-pencil leading-relaxed pt-2">
                  Export all internship applications with posting details, organization names,
                  applicant names, application status, and review timestamps.
                </p>
              </div>

              <div>
                <a
                  href="/api/admin/reports/applications.csv"
                  download="applications_report.csv"
                  className="inline-flex items-center gap-2 justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-petrol text-surface hover:bg-petrol-hover"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </a>
              </div>
            </div>
          )}

          {/* Users Report: Admin Only */}
          {isAdmin && (
            <div
              data-testid="users-report-card"
              className="p-6 bg-surface border border-line rounded-control flex flex-col justify-between space-y-4 shadow-none"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-chalk text-petrol flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-ink">User accounts</h3>
                    <p className="text-xs text-pencil">Platform user registry and audit data</p>
                  </div>
                </div>
                <p className="text-sm text-pencil leading-relaxed pt-2">
                  Export all registered user profiles with user ID, name, email, role, active
                  status, and creation date. Excludes passwords and session secrets.
                </p>
              </div>

              <div>
                <a
                  href="/api/admin/reports/users.csv"
                  download="users_report.csv"
                  className="inline-flex items-center gap-2 justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-petrol text-surface hover:bg-petrol-hover"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
};
