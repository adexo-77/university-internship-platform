import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { HealthCheck } from './HealthCheck';

describe('HealthCheck Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls /api/health and displays "API: ok" when the server is healthy', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();

      if (url.includes('/api/health/db')) {
        return Promise.resolve(
          new Response(JSON.stringify({ database: 'ok' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }

      if (url.includes('/api/health')) {
        return Promise.resolve(
          new Response(JSON.stringify({ status: 'ok' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }

      return Promise.reject(new Error('Unknown URL'));
    });

    render(<HealthCheck />);

    // Expect "API: ok" to appear after fetching
    await waitFor(() => {
      expect(screen.getByText('API: ok')).toBeInTheDocument();
    });

    expect(screen.getByText('Database: ok')).toBeInTheDocument();
    expect(screen.getByText('Operational')).toBeInTheDocument();
  });

  it('displays error details when /api/health call fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();

      if (url.includes('/api/health')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: 'Service Unavailable' }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }

      return Promise.reject(new Error('Network error'));
    });

    render(<HealthCheck />);

    await waitFor(() => {
      expect(screen.getByText(/API Error:/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Unavailable')).toBeInTheDocument();
  });
});
