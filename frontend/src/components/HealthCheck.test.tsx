import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HealthCheck } from './HealthCheck';

describe('HealthCheck Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls /api/health and displays "API: ok" and "Operational" badges when healthy', async () => {
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

    await waitFor(() => {
      expect(screen.getByText('API: ok')).toBeInTheDocument();
    });

    expect(screen.getByText('Database: ok')).toBeInTheDocument();
    const operationalBadges = screen.getAllByText('Operational');
    expect(operationalBadges.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole('button', { name: 'Check again' })).toBeInTheDocument();
  });

  it('displays actionable error explanation when /api/health fails', async () => {
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
      expect(
        screen.getByText('Could not reach the core API server at /api/health.')
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText(/Ensure the backend development server is running on port 8001/i)
    ).toBeInTheDocument();
  });

  it('triggers a status recheck when "Check again" is clicked', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation(() => {
      return Promise.resolve(
        new Response(JSON.stringify({ status: 'ok' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    render(<HealthCheck />);

    await waitFor(() => {
      expect(screen.getByText('API: ok')).toBeInTheDocument();
    });

    const checkAgainBtn = screen.getByRole('button', { name: 'Check again' });
    fireEvent.click(checkAgainBtn);

    expect(fetchSpy).toHaveBeenCalled();
  });
});
