import React from 'react';
import { HealthCheck } from '../components/HealthCheck';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui';

export const SystemStatusPage: React.FC = () => {
  return (
    <AppShell>
      <div className="space-y-8">
        <PageHeader
          title="System status"
          description="Operational verification and connectivity status for platform services."
        />
        <HealthCheck />
      </div>
    </AppShell>
  );
};
