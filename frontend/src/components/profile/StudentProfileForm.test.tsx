import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { StudentProfileForm } from './StudentProfileForm';

describe('StudentProfileForm Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('loads and displays student profile fields', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/students/me')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 1,
              user_id: 10,
              university: 'Stanford University',
              department: 'Computer Science',
              year_of_study: 3,
              bio: 'Passionate about systems.',
              skills: ['Python', 'SQL'],
              updated_at: '2026-10-18T00:00:00Z',
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(<StudentProfileForm />);

    expect(screen.getByTestId('profile-loading-state')).toBeInTheDocument();

    expect(await screen.findByLabelText('University')).toHaveValue('Stanford University');
    expect(screen.getByLabelText('Department')).toHaveValue('Computer Science');
    expect(screen.getByLabelText('Year of study')).toHaveValue('3');
    expect(screen.getByLabelText('Bio')).toHaveValue('Passionate about systems.');
    expect(screen.getByLabelText('Skills')).toHaveValue('Python, SQL');
  });

  it('saves student profile successfully and shows success notice', async () => {
    let capturedBody: unknown = null;

    vi.spyOn(globalThis, 'fetch').mockImplementation(
      (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();
        if (url.includes('/api/students/me')) {
          if (init?.method === 'PUT') {
            capturedBody = JSON.parse(init.body as string);
            return Promise.resolve(
              new Response(
                JSON.stringify({
                  id: 1,
                  user_id: 10,
                  university: 'MIT',
                  department: 'EECS',
                  year_of_study: 4,
                  bio: 'Updated bio',
                  skills: ['Python', 'React'],
                  updated_at: '2026-10-18T00:00:00Z',
                }),
                { status: 200, headers: { 'Content-Type': 'application/json' } }
              )
            );
          }
          return Promise.resolve(
            new Response(
              JSON.stringify({
                id: 1,
                user_id: 10,
                university: '',
                department: '',
                year_of_study: null,
                bio: '',
                skills: [],
                updated_at: '2026-10-18T00:00:00Z',
              }),
              { status: 200, headers: { 'Content-Type': 'application/json' } }
            )
          );
        }
        return Promise.reject(new Error(`Unknown url: ${url}`));
      }
    );

    render(<StudentProfileForm />);

    expect(await screen.findByLabelText('University')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('University'), { target: { value: 'MIT' } });
    fireEvent.change(screen.getByLabelText('Department'), { target: { value: 'EECS' } });
    fireEvent.change(screen.getByLabelText('Year of study'), { target: { value: '4' } });
    fireEvent.change(screen.getByLabelText('Bio'), { target: { value: 'Updated bio' } });
    fireEvent.change(screen.getByLabelText('Skills'), { target: { value: 'Python, React' } });

    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));

    await waitFor(() => {
      expect(screen.getByTestId('profile-success-notice')).toHaveTextContent('Profile saved');
    });

    expect(capturedBody).toEqual({
      university: 'MIT',
      department: 'EECS',
      year_of_study: 4,
      bio: 'Updated bio',
      skills: ['Python', 'React'],
    });
  });

  it('displays plain error notice when server rejects update', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();
        if (url.includes('/api/students/me')) {
          if (init?.method === 'PUT') {
            return Promise.resolve(
              new Response(
                JSON.stringify({
                  detail: 'At most 20 skills are permitted.',
                  code: 'VALIDATION_ERROR',
                }),
                { status: 422, headers: { 'Content-Type': 'application/json' } }
              )
            );
          }
          return Promise.resolve(
            new Response(
              JSON.stringify({
                id: 1,
                user_id: 10,
                university: null,
                department: null,
                year_of_study: null,
                bio: null,
                skills: [],
                updated_at: '2026-10-18T00:00:00Z',
              }),
              { status: 200, headers: { 'Content-Type': 'application/json' } }
            )
          );
        }
        return Promise.reject(new Error(`Unknown url: ${url}`));
      }
    );

    render(<StudentProfileForm />);

    expect(await screen.findByLabelText('University')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));

    await waitFor(() => {
      expect(screen.getByTestId('profile-server-error')).toHaveTextContent(
        'At most 20 skills are permitted.'
      );
    });
  });

  it('displays error notice when loading profile fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/students/me')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: 'Failed to connect', code: 'DB_ERROR' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(<StudentProfileForm />);

    await waitFor(() => {
      expect(screen.getByTestId('profile-load-error')).toHaveTextContent('Failed to connect');
    });
  });
});
