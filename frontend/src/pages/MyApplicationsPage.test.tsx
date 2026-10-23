import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import * as applicationApi from '../api/application';
import { AuthProvider } from '../context/AuthContext';
import { MyApplicationsPage } from './MyApplicationsPage';
import { Application } from '../types/application';
import { User } from '../types/auth';

vi.mock('../api/application', () => ({
  getStudentApplications: vi.fn(),
  withdrawApplication: vi.fn(),
}));

const mockStudentUser: User = {
  id: 20,
  email: 'student@test.com',
  full_name: 'Student Candidate',
  role: 'student',
  is_active: true,
  created_at: '2026-10-20T10:00:00Z',
  updated_at: '2026-10-20T10:00:00Z',
};

const mockApp: Application = {
  id: 501,
  posting_id: 101,
  posting_title: 'Frontend Intern',
  organization_name: 'Acme Corp',
  student_id: 20,
  cover_letter: 'Passionate about React.',
  status: 'submitted',
  decision_message: null,
  decided_at: null,
  created_at: '2026-10-20T12:00:00Z',
  updated_at: '2026-10-20T12:00:00Z',
};

describe('MyApplicationsPage Component', () => {
  it('renders applications table and opens in-app confirm modal on withdraw click', async () => {
    vi.mocked(applicationApi.getStudentApplications).mockResolvedValue([mockApp]);
    vi.mocked(applicationApi.withdrawApplication).mockResolvedValue({
      ...mockApp,
      status: 'withdrawn',
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockStudentUser}>
          <MyApplicationsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByText('Frontend Intern')).toBeInTheDocument();
    expect(screen.getByText('Acme Corp')).toBeInTheDocument();

    const withdrawBtn = screen.getByRole('button', { name: /withdraw/i });
    fireEvent.click(withdrawBtn);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(
      screen.getByText(/are you sure you want to withdraw this application\?/i)
    ).toBeInTheDocument();

    const confirmBtn = within(dialog).getByRole('button', { name: /^withdraw$/i });
    fireEvent.click(confirmBtn);

    expect(applicationApi.withdrawApplication).toHaveBeenCalledWith(501);
  });
});
