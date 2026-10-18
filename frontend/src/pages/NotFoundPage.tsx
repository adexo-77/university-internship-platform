import React from 'react';
import { Link } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Button, EmptyState } from '../components/ui';
import { useAuth } from '../hooks/useAuth';

export const NotFoundPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  const content = (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <EmptyState
        title="Page not found"
        description="The page you requested does not exist on this platform."
        action={
          <Link to={isAuthenticated ? '/account' : '/login'}>
            <Button variant="secondary">
              {isAuthenticated ? 'Return to account' : 'Return to log in'}
            </Button>
          </Link>
        }
      />
    </div>
  );

  if (isAuthenticated) {
    return <AppShell>{content}</AppShell>;
  }

  return (
    <div className="min-h-screen bg-chalk flex items-center justify-center p-4">{content}</div>
  );
};
