import React from 'react';
import { Link, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/auth';
import { AppShell } from '../layout/AppShell';
import { Button, Notice, PageHeader } from '../ui';

export interface RoleRouteProps {
  allowedRoles: UserRole[];
  children?: React.ReactNode;
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
            title="Access restricted"
            description="Your account role does not have authorization to view this resource."
          />
          <Notice variant="attention" title="Permission required">
            You don't have access to this page.
          </Notice>
          <div>
            <Link to="/account">
              <Button variant="secondary">Return to account</Button>
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  return children ? <>{children}</> : <Outlet />;
};
