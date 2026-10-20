import React from 'react';
import { formatDate } from '../../lib/dates';
import { AdminUser } from '../../types/admin';
import { Badge, Button, Column, DataTable } from '../ui';

export interface AdminUsersTableProps {
  users: AdminUser[];
  onToggleStatus: (user: AdminUser) => void;
  onResetPassword: (user: AdminUser) => void;
  emptyMessage?: string;
}

export const AdminUsersTable: React.FC<AdminUsersTableProps> = ({
  users,
  onToggleStatus,
  onResetPassword,
  emptyMessage = 'No users found matching your search.',
}) => {
  const columns: Column<AdminUser>[] = [
    {
      key: 'name',
      header: 'Name',
      render: (user) => <span className="font-medium text-ink">{user.full_name}</span>,
    },
    {
      key: 'email',
      header: 'Email',
      render: (user) => <span className="font-mono text-xs text-pencil">{user.email}</span>,
    },
    {
      key: 'role',
      header: 'Role',
      render: (user) => <Badge variant="neutral">{user.role}</Badge>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (user) => (
        <Badge variant={user.is_active ? 'success' : 'error'}>
          {user.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (user) => <span className="text-pencil text-sm">{formatDate(user.created_at)}</span>,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (user) => (
        <div className="flex items-center gap-2">
          <Button type="button" variant="quiet" size="sm" onClick={() => onToggleStatus(user)}>
            {user.is_active ? 'Deactivate' : 'Activate'}
          </Button>
          <Button type="button" variant="quiet" size="sm" onClick={() => onResetPassword(user)}>
            Reset password
          </Button>
        </div>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={users}
      keyExtractor={(user) => String(user.id)}
      emptyMessage={emptyMessage}
    />
  );
};
