import React, { useCallback, useEffect, useState } from 'react';
import { listAdminOrganizations, updateAdminOrganizationApproval } from '../api/admin_organization';
import { AdminOrganizationApprovalModal } from '../components/admin/AdminOrganizationApprovalModal';
import { AdminOrganizationsTable } from '../components/admin/AdminOrganizationsTable';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader, Select } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { AdminOrganizationItem } from '../types/admin';
import { ApprovalStatus } from '../types/profile';

const PAGE_SIZE = 10;

export const AdminOrganizationsPage: React.FC = () => {
  usePageTitle('Organizations');

  const [organizations, setOrganizations] = useState<AdminOrganizationItem[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [modalTarget, setModalTarget] = useState<AdminOrganizationItem | null>(null);
  const [targetStatus, setTargetStatus] = useState<ApprovalStatus | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  const fetchOrganizations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAdminOrganizations({
        approval_status: statusFilter === 'all' ? undefined : statusFilter,
        limit: PAGE_SIZE,
        offset,
      });
      setOrganizations(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load organizations.');
      }
    } finally {
      setLoading(false);
    }
  }, [statusFilter, offset]);

  useEffect(() => {
    fetchOrganizations();
  }, [fetchOrganizations]);

  const handleOpenApprove = (org: AdminOrganizationItem) => {
    setModalError(null);
    setTargetStatus('approved');
    setModalTarget(org);
  };

  const handleOpenReject = (org: AdminOrganizationItem) => {
    setModalError(null);
    setTargetStatus('rejected');
    setModalTarget(org);
  };

  const handleConfirmApproval = async (status: ApprovalStatus, note: string) => {
    if (!modalTarget) return;
    setIsSubmitting(true);
    setModalError(null);
    try {
      await updateAdminOrganizationApproval(modalTarget.user_id, {
        approval_status: status,
        approval_note: note || null,
      });
      setSuccessNotice(`Organization ${modalTarget.organization_name} has been ${status}.`);
      setModalTarget(null);
      setTargetStatus(null);
      await fetchOrganizations();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setModalError(err.message);
      } else {
        setModalError('Failed to update organization approval status.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Organization approvals"
          description="Review registered organization profiles, verify details, and grant publishing permissions."
        />

        {successNotice && (
          <div className="rounded-control border border-petrol bg-petrol-tint p-4 text-sm text-ink flex items-center justify-between">
            <span>{successNotice}</span>
            <button
              type="button"
              className="text-pencil hover:text-ink text-xs underline"
              onClick={() => setSuccessNotice(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="w-full sm:w-64">
            <Select
              id="organization-status-filter"
              label="Approval status filter"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setOffset(0);
              }}
              options={[
                { value: 'pending', label: 'Pending (Default)' },
                { value: 'approved', label: 'Approved' },
                { value: 'rejected', label: 'Rejected' },
                { value: 'all', label: 'All organizations' },
              ]}
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading organizations...</div>
        ) : (
          <div className="space-y-4">
            <AdminOrganizationsTable
              organizations={organizations}
              onApprove={handleOpenApprove}
              onReject={handleOpenReject}
            />

            <div className="flex items-center justify-between pt-2">
              <span className="text-sm text-pencil">
                Showing {total === 0 ? 0 : offset + 1} to {Math.min(offset + PAGE_SIZE, total)} of{' '}
                {total} organizations
              </span>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="quiet"
                  size="sm"
                  disabled={offset === 0}
                  onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
                >
                  Previous
                </Button>
                <Button
                  type="button"
                  variant="quiet"
                  size="sm"
                  disabled={offset + PAGE_SIZE >= total}
                  onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        )}

        <AdminOrganizationApprovalModal
          org={modalTarget}
          targetStatus={targetStatus}
          isOpen={Boolean(modalTarget && targetStatus)}
          onClose={() => {
            setModalTarget(null);
            setTargetStatus(null);
          }}
          onConfirm={handleConfirmApproval}
          isSubmitting={isSubmitting}
          error={modalError}
        />
      </div>
    </AppShell>
  );
};
