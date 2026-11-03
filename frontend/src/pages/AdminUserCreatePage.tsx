import React from 'react';
import { AdminUserForm } from '../components/admin/AdminUserForm';
import { AppShell } from '../components/layout/AppShell';
import { BackLink, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';

export const AdminUserCreatePage: React.FC = () => {
  usePageTitle('New user');

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <div>
          <BackLink to="/admin/users" label="Back to Users" />
          <PageHeader
            title="Create user"
            description="Provision a new instructor or administrator account with credentials."
          />
        </div>

        <AdminUserForm />
      </div>
    </AppShell>
  );
};
