import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { OrganizationProfileForm } from './OrganizationProfileForm';

describe('OrganizationProfileForm Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('loads and displays organization profile fields', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/organizations/me')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 2,
              user_id: 20,
              organization_name: 'Acme Robotics',
              industry: 'Hardware & AI',
              location: 'Boston, MA',
              website: 'https://acme.org',
              description: 'Innovating robotics.',
              updated_at: '2026-10-18T00:00:00Z',
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(<OrganizationProfileForm />);

    expect(screen.getByTestId('profile-loading-state')).toBeInTheDocument();

    expect(await screen.findByLabelText(/organization name/i)).toHaveValue('Acme Robotics');
    expect(screen.getByLabelText('Industry')).toHaveValue('Hardware & AI');
    expect(screen.getByLabelText('Location')).toHaveValue('Boston, MA');
    expect(screen.getByLabelText('Website')).toHaveValue('https://acme.org');
    expect(screen.getByLabelText('Description')).toHaveValue('Innovating robotics.');
  });

  it('saves organization profile successfully and shows success notice', async () => {
    let capturedBody: unknown = null;

    vi.spyOn(globalThis, 'fetch').mockImplementation(
      (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();
        if (url.includes('/api/organizations/me')) {
          if (init?.method === 'PUT') {
            capturedBody = JSON.parse(init.body as string);
            return Promise.resolve(
              new Response(
                JSON.stringify({
                  id: 2,
                  user_id: 20,
                  organization_name: 'Acme Global',
                  industry: 'Logistics',
                  location: 'Nairobi',
                  website: 'https://acme.global',
                  description: 'Global reach',
                  updated_at: '2026-10-18T00:00:00Z',
                }),
                { status: 200, headers: { 'Content-Type': 'application/json' } }
              )
            );
          }
          return Promise.resolve(
            new Response(
              JSON.stringify({
                id: 2,
                user_id: 20,
                organization_name: 'Acme Initial',
                industry: null,
                location: null,
                website: null,
                description: null,
                updated_at: '2026-10-18T00:00:00Z',
              }),
              { status: 200, headers: { 'Content-Type': 'application/json' } }
            )
          );
        }
        return Promise.reject(new Error(`Unknown url: ${url}`));
      }
    );

    render(<OrganizationProfileForm />);

    expect(await screen.findByLabelText(/organization name/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { value: 'Acme Global' },
    });
    fireEvent.change(screen.getByLabelText('Industry'), { target: { value: 'Logistics' } });
    fireEvent.change(screen.getByLabelText('Location'), { target: { value: 'Nairobi' } });
    fireEvent.change(screen.getByLabelText('Website'), {
      target: { value: 'https://acme.global' },
    });
    fireEvent.change(screen.getByLabelText('Description'), {
      target: { value: 'Global reach' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));

    await waitFor(() => {
      expect(screen.getByTestId('profile-success-notice')).toHaveTextContent('Profile saved');
    });

    expect(capturedBody).toEqual({
      organization_name: 'Acme Global',
      industry: 'Logistics',
      location: 'Nairobi',
      website: 'https://acme.global',
      description: 'Global reach',
    });
  });

  it('validates required organization name on client before saving', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/organizations/me')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 2,
              user_id: 20,
              organization_name: 'Existing Org',
              industry: null,
              location: null,
              website: null,
              description: null,
              updated_at: '2026-10-18T00:00:00Z',
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(<OrganizationProfileForm />);

    expect(await screen.findByLabelText(/organization name/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { value: '' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));

    expect(await screen.findByText('Organization name cannot be blank.')).toBeInTheDocument();
  });
});
