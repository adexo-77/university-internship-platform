import React from 'react';
import { useHealth } from '../hooks/useHealth';
import { Badge, Button, Column, DataTable, ErrorMessage } from './ui';

interface ServiceStatusRow {
  key: string;
  service: string;
  route: string;
  status: 'Operational' | 'Unavailable' | 'Checking';
  response: string;
}

export const HealthCheck: React.FC = () => {
  const { apiStatus, dbStatus, isLoading, error, refetch } = useHealth();

  const isApiOk = apiStatus === 'ok';
  const isDbOk = dbStatus === 'ok';

  const rows: ServiceStatusRow[] = [
    {
      key: 'api',
      service: 'Core API',
      route: '/api/health',
      status: isLoading ? 'Checking' : isApiOk ? 'Operational' : 'Unavailable',
      response: isLoading
        ? 'Pending response'
        : isApiOk
          ? 'API: ok'
          : (error ?? 'Connection failed'),
    },
    {
      key: 'db',
      service: 'PostgreSQL database',
      route: '/api/health/db',
      status: isLoading ? 'Checking' : isDbOk ? 'Operational' : 'Unavailable',
      response: isLoading
        ? 'Pending query'
        : isDbOk
          ? 'Database: ok'
          : (dbStatus ?? 'Connection failed'),
    },
  ];

  const columns: Column<ServiceStatusRow>[] = [
    {
      key: 'service',
      header: 'Service',
      render: (item) => <span className="font-medium text-ink">{item.service}</span>,
    },
    {
      key: 'route',
      header: 'Endpoint route',
      render: (item) => <code className="text-pencil text-xs">{item.route}</code>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => {
        if (item.status === 'Operational') {
          return <Badge variant="success">Operational</Badge>;
        }
        if (item.status === 'Unavailable') {
          return <Badge variant="error">Unavailable</Badge>;
        }
        return <Badge variant="attention">Checking</Badge>;
      },
    },
    {
      key: 'response',
      header: 'Response',
      render: (item) => (
        <span
          className={
            item.status === 'Operational'
              ? 'text-pencil'
              : item.status === 'Unavailable'
                ? 'text-brick'
                : 'text-pencil'
          }
        >
          {item.response}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-ink">Services and dependencies</h2>
          <p className="text-xs text-pencil mt-0.5 max-w-[75ch]">
            Status of the local application server and backend database connection.
          </p>
        </div>

        <Button
          id="check-again-button"
          variant="secondary"
          size="sm"
          onClick={() => void refetch()}
          disabled={isLoading}
        >
          {isLoading ? 'Checking...' : 'Check again'}
        </Button>
      </div>

      <DataTable columns={columns} data={rows} keyExtractor={(item) => item.key} />

      {error && (
        <ErrorMessage
          whatHappened="Could not reach the core API server at /api/health."
          howToFix="Ensure the backend development server is running on port 8001 using 'python -m uvicorn app.main:app --port 8001' and verify that your proxy configuration in vite.config.ts points to http://localhost:8001."
          action={
            <Button variant="secondary" size="sm" onClick={() => void refetch()}>
              Check again
            </Button>
          }
        />
      )}

      {!error && !isDbOk && dbStatus && (
        <ErrorMessage
          whatHappened={`Database query test failed: ${dbStatus}`}
          howToFix="Verify that PostgreSQL is running locally and that DATABASE_URL and TEST_DATABASE_URL in .env match your database credentials. Run 'psql -U postgres' or check Windows Services."
          action={
            <Button variant="secondary" size="sm" onClick={() => void refetch()}>
              Check again
            </Button>
          }
        />
      )}
    </div>
  );
};
