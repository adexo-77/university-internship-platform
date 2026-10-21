import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStudentApplications, withdrawApplication } from '../api/application';
import { MyApplicationsTable } from '../components/internships/MyApplicationsTable';
import { AppShell } from '../components/layout/AppShell';
import { Button, ConfirmModal, ErrorMessage, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { Application } from '../types/application';

export const MyApplicationsPage: React.FC = () => {
  usePageTitle('My applications');
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [withdrawingId, setWithdrawingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchApps = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStudentApplications();
      setApplications(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load applications.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchApps();
  }, [fetchApps]);

  const [pendingWithdrawId, setPendingWithdrawId] = useState<number | null>(null);

  const handleConfirmWithdraw = async () => {
    if (!pendingWithdrawId) return;
    const id = pendingWithdrawId;
    setPendingWithdrawId(null);
    setWithdrawingId(id);
    setError(null);
    try {
      await withdrawApplication(id);
      await fetchApps();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to withdraw application.');
      }
    } finally {
      setWithdrawingId(null);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <PageHeader
            title="My applications"
            description="Track the status and review decisions for your submitted applications."
          />
          <Button type="button" variant="secondary" onClick={() => navigate('/internships')}>
            Browse internships
          </Button>
        </div>

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading your applications...</div>
        ) : (
          <MyApplicationsTable
            applications={applications}
            onWithdraw={(id) => setPendingWithdrawId(id)}
            isWithdrawing={withdrawingId}
            emptyMessage="You have not submitted any internship applications yet."
          />
        )}

        <ConfirmModal
          isOpen={pendingWithdrawId !== null}
          title="Withdraw application"
          message="Are you sure you want to withdraw this application?"
          confirmLabel="Withdraw"
          confirmVariant="danger"
          onClose={() => setPendingWithdrawId(null)}
          onConfirm={handleConfirmWithdraw}
        />
      </div>
    </AppShell>
  );
};
