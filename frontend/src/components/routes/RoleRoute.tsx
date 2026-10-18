import React from 'react';
import { Link, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/auth';
import { AppShell } from '../layout/AppShell';
import { Button, PageHeader } from '../ui';

export interface RoleRouteProps {
  allowedRoles: UserRole[];
  children?: React.ReactNode;
}

/**
 * Formats a list of role names into a readable string.
 * Example: ['admin'] → "admin", ['admin', 'instructor'] → "admin and instructor".
 */
function formatRoleNames(roles: UserRole[]): string {
  if (roles.length <= 1) {
    return roles.join('');
  }
  return `${roles.slice(0, -1).join(', ')} and ${roles[roles.length - 1]}`;
}

export const RoleRoute: React.FC<RoleRouteProps> = ({ allowedRoles, children }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return (
      <AppShell>
        <div className="space-y-6 max-w-2xl">
          <PageHeader
            title="You don't have access to this page"
            description={`This page is only available to ${formatRoleNames(allowedRoles)} accounts.`}
          />
          <div>
            <Link to="/account">
              <Button variant="secondary">Go to your account</Button>
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  return children ? <>{children}</> : <Outlet />;
};
