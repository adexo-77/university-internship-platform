import React from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Column, DataTable, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';

interface AccountFieldRow {
  key: string;
  field: string;
  value: React.ReactNode;
}

export const AccountPage: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  const rows: AccountFieldRow[] = [
    {
      key: 'name',
      field: 'Full name',
      value: <span className="font-medium text-ink">{user.full_name}</span>,
    },
    {
      key: 'email',
      field: 'Email address',
      value: <span className="text-pencil font-mono text-xs">{user.email}</span>,
    },
    {
      key: 'role',
      field: 'Account role',
      value: <Badge variant="neutral">{user.role}</Badge>,
    },
    {
      key: 'status',
      field: 'Status',
      value: (
        <Badge variant={user.is_active ? 'success' : 'error'}>
          {user.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
  ];

  const columns: Column<AccountFieldRow>[] = [
    {
      key: 'field',
      header: 'Property',
      render: (item) => <span className="font-medium text-ink">{item.field}</span>,
    },
    {
      key: 'value',
      header: 'Details',
      render: (item) => item.value,
    },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Account profile"
          description="Personal details, platform permissions, and credential status for your account."
        />

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-ink">Account details</h2>
          </div>
          <DataTable columns={columns} data={rows} keyExtractor={(item) => item.key} />
        </div>
      </div>
    </AppShell>
  );
};
