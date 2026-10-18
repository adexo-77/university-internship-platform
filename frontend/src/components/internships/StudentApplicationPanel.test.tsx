import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Application } from '../../types/application';
import { Internship } from '../../types/internship';
import { StudentApplicationPanel } from './StudentApplicationPanel';

const mockInternship: Internship = {
  id: 1,
  organization_id: 5,
  title: 'QA Engineer Intern',
  description: 'Test automation.',
  requirements: 'Python & Playwright.',
  location: 'Remote',
  work_mode: 'remote',
  application_deadline: '2028-01-01T00:00:00Z',
  status: 'open',
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
  applications_accepted: true,
};

describe('StudentApplicationPanel Component', () => {
  it('renders incomplete profile notice with link to profile', () => {
    render(
      <MemoryRouter>
        <StudentApplicationPanel
          internship={mockInternship}
          myApp={null}
          isProfileComplete={false}
          submitting={false}
          error={null}
          onApply={vi.fn()}
          onWithdraw={vi.fn()}
        />
      </MemoryRouter>
    );

    expect(screen.getByText(/complete your profile before applying/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /go to profile/i })).toHaveAttribute(
      'href',
      '/profile'
    );
  });

  it('renders applications closed notice after deadline or when closed', () => {
    const closedPosting: Internship = {
      ...mockInternship,
      applications_accepted: false,
    };

    render(
      <MemoryRouter>
        <StudentApplicationPanel
          internship={closedPosting}
          myApp={null}
          isProfileComplete={true}
          submitting={false}
          error={null}
          onApply={vi.fn()}
          onWithdraw={vi.fn()}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Applications closed')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Submit application' })).not.toBeInTheDocument();
  });

  it('renders apply form when eligible and not yet applied', () => {
    render(
      <MemoryRouter>
        <StudentApplicationPanel
          internship={mockInternship}
          myApp={null}
          isProfileComplete={true}
          submitting={false}
          error={null}
          onApply={vi.fn()}
          onWithdraw={vi.fn()}
        />
      </MemoryRouter>
    );

    expect(screen.getByRole('button', { name: 'Submit application' })).toBeInTheDocument();
  });

  it('renders application status and withdraw action when already applied', () => {
    const submittedApp: Application = {
      id: 42,
      posting_id: 1,
      student_id: 99,
      cover_letter: 'My qualifications...',
      status: 'submitted',
      created_at: '2026-10-18T00:00:00Z',
      updated_at: '2026-10-18T00:00:00Z',
    };

    const handleWithdraw = vi.fn();
    render(
      <MemoryRouter>
        <StudentApplicationPanel
          internship={mockInternship}
          myApp={submittedApp}
          isProfileComplete={true}
          submitting={false}
          error={null}
          onApply={vi.fn()}
          onWithdraw={handleWithdraw}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Submitted')).toBeInTheDocument();
    const withdrawBtn = screen.getByRole('button', { name: 'Withdraw' });
    expect(withdrawBtn).toBeInTheDocument();

    fireEvent.click(withdrawBtn);
    expect(handleWithdraw).toHaveBeenCalled();
  });
});
