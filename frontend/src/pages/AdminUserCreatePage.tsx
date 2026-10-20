import React from 'react';
import { Link } from 'react-router-dom';
import { AdminUserForm } from '../components/admin/AdminUserForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';

export const AdminUserCreatePage: React.FC = () => {
  usePageTitle('New user');

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <div>
          <Link
            to="/admin/users"
            className="text-sm text-petrol hover:underline font-medium mb-2 inline-block"
          >
            &larr; Back to users
          </Link>
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
