import React, { useCallback, useEffect, useState } from 'react';
import {
  getAdminDashboard,
  getCoordinatorDashboard,
  getInstructorDashboard,
  getOrganizationDashboard,
  getStudentDashboard,
} from '../api/dashboard';
import { AdminDashboard } from '../components/dashboard/AdminDashboard';
import { CoordinatorDashboard } from '../components/dashboard/CoordinatorDashboard';
import { InstructorDashboard } from '../components/dashboard/InstructorDashboard';
import { OrganizationDashboard } from '../components/dashboard/OrganizationDashboard';
import { StudentDashboard } from '../components/dashboard/StudentDashboard';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import {
  AdminDashboardResponse,
  CoordinatorDashboardResponse,
  InstructorDashboardResponse,
  OrganizationDashboardResponse,
  StudentDashboardResponse,
} from '../types/dashboard';

type DashboardData =
  | { role: 'student'; data: StudentDashboardResponse }
  | { role: 'instructor'; data: InstructorDashboardResponse }
  | { role: 'organization'; data: OrganizationDashboardResponse }
  | { role: 'admin'; data: AdminDashboardResponse }
  | { role: 'coordinator'; data: CoordinatorDashboardResponse };

export const DashboardPage: React.FC = () => {
  usePageTitle('Dashboard');
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);

    try {
      if (user.role === 'student') {
        const res = await getStudentDashboard();
        setData({ role: 'student', data: res });
      } else if (user.role === 'instructor') {
        const res = await getInstructorDashboard();
        setData({ role: 'instructor', data: res });
      } else if (user.role === 'organization') {
        const res = await getOrganizationDashboard();
        setData({ role: 'organization', data: res });
      } else if (user.role === 'admin') {
        const res = await getAdminDashboard();
        setData({ role: 'admin', data: res });
      } else if (user.role === 'coordinator') {
        const res = await getCoordinatorDashboard();
        setData({ role: 'coordinator', data: res });
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load dashboard.');
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Dashboard"
          description="Overview of your current coursework, applications, and action items."
        />

        {loading && (
          <div className="py-12 text-center text-sm text-pencil">Loading dashboard...</div>
        )}

        {error && !loading && (
          <ErrorMessage
            whatHappened={error}
            howToFix="Please check your connection and try loading your dashboard again."
            action={
              <Button variant="secondary" onClick={() => void loadDashboard()}>
                Retry
              </Button>
            }
          />
        )}

        {!loading && !error && data && (
          <>
            {data.role === 'student' && <StudentDashboard data={data.data} />}
            {data.role === 'instructor' && <InstructorDashboard data={data.data} />}
            {data.role === 'organization' && <OrganizationDashboard data={data.data} />}
            {data.role === 'admin' && <AdminDashboard data={data.data} />}
            {data.role === 'coordinator' && <CoordinatorDashboard data={data.data} />}
          </>
        )}
      </div>
    </AppShell>
  );
};
