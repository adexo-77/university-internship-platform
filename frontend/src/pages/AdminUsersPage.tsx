import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listAdminUsers, updateAdminUserStatus } from '../api/admin_user';
import { AdminResetPasswordModal } from '../components/admin/AdminResetPasswordModal';
import { AdminUsersTable } from '../components/admin/AdminUsersTable';
import { AdminUserStatusModal } from '../components/admin/AdminUserStatusModal';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader, Select, TextField } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { AdminUser } from '../types/admin';

const PAGE_SIZE = 10;

export const AdminUsersPage: React.FC = () => {
  usePageTitle('Users');
  const navigate = useNavigate();

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [statusTarget, setStatusTarget] = useState<AdminUser | null>(null);
  const [isStatusSubmitting, setIsStatusSubmitting] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  const [passwordTarget, setPasswordTarget] = useState<AdminUser | null>(null);
  const [actionSuccessNotice, setActionSuccessNotice] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAdminUsers({
        q: searchQuery.trim() || undefined,
        role: roleFilter || undefined,
        limit: PAGE_SIZE,
        offset,
      });
      setUsers(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load users.');
      }
    } finally {
      setLoading(false);
    }
  }, [searchQuery, roleFilter, offset]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleToggleStatusConfirm = async () => {
    if (!statusTarget) return;
    setIsStatusSubmitting(true);
    setStatusError(null);
    try {
      await updateAdminUserStatus(statusTarget.id, !statusTarget.is_active);
      setActionSuccessNotice(
        `User ${statusTarget.full_name} successfully ${statusTarget.is_active ? 'deactivated' : 'activated'}.`
      );
      setStatusTarget(null);
      await fetchUsers();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setStatusError(err.message);
      } else {
        setStatusError('Failed to update user status.');
      }
    } finally {
      setIsStatusSubmitting(false);
    }
  };

  const handlePasswordResetSuccess = (user: AdminUser) => {
    setActionSuccessNotice(`Password for ${user.full_name} (${user.email}) successfully reset.`);
    fetchUsers();
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <PageHeader
            title="User management"
            description="Manage platform user accounts, active statuses, roles, and credentials."
          />
          <Button type="button" variant="primary" onClick={() => navigate('/admin/users/new')}>
            New user
          </Button>
        </div>

        {actionSuccessNotice && (
          <div className="rounded-control border border-petrol bg-petrol-tint p-4 text-sm text-ink flex items-center justify-between">
            <span>{actionSuccessNotice}</span>
            <button
              type="button"
              className="text-pencil hover:text-ink text-xs underline"
              onClick={() => setActionSuccessNotice(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <div className="flex-1">
            <TextField
              id="search-users"
              label="Search users"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setOffset(0);
              }}
              placeholder="Search by name or email..."
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              id="role-filter"
              label="Role filter"
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value);
                setOffset(0);
              }}
              options={[
                { value: '', label: 'All roles' },
                { value: 'instructor', label: 'Instructor' },
                { value: 'admin', label: 'Admin' },
                { value: 'student', label: 'Student' },
                { value: 'organization', label: 'Organization' },
              ]}
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading users...</div>
        ) : (
          <div className="space-y-4">
            <AdminUsersTable
              users={users}
              onToggleStatus={(u) => {
                setStatusError(null);
                setStatusTarget(u);
              }}
              onResetPassword={(u) => setPasswordTarget(u)}
            />

            <div className="flex items-center justify-between pt-2">
              <span className="text-sm text-pencil">
                Showing {total === 0 ? 0 : offset + 1} to {Math.min(offset + PAGE_SIZE, total)} of{' '}
                {total} users
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

        <AdminUserStatusModal
          user={statusTarget}
          isOpen={Boolean(statusTarget)}
          onClose={() => setStatusTarget(null)}
          onConfirm={handleToggleStatusConfirm}
          isSubmitting={isStatusSubmitting}
          error={statusError}
        />

        <AdminResetPasswordModal
          user={passwordTarget}
          isOpen={Boolean(passwordTarget)}
          onClose={() => setPasswordTarget(null)}
          onSuccess={handlePasswordResetSuccess}
        />
      </div>
    </AppShell>
  );
};
