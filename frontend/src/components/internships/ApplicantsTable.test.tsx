import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Application } from '../../types/application';
import { ApplicantsTable } from './ApplicantsTable';

describe('ApplicantsTable Component', () => {
  it('renders empty message when no applications exist', () => {
    render(
      <MemoryRouter>
        <ApplicantsTable applications={[]} />
      </MemoryRouter>
    );

    expect(screen.getByText('No applications submitted yet.')).toBeInTheDocument();
  });

  it('renders applicant roster rows with details and review links', () => {
    const mockApplications: Application[] = [
      {
        id: 101,
        posting_id: 1,
        student_id: 201,
        cover_letter: 'Cover letter content...',
        status: 'submitted',
        created_at: '2026-10-18T00:00:00Z',
        updated_at: '2026-10-18T00:00:00Z',
        applicant: {
          user_id: 201,
          full_name: 'Alex Developer',
          email: 'alex@univ.edu',
          university: 'Nairobi University',
          department: 'Computer Science',
          year_of_study: 4,
          skills: ['Python', 'Django'],
        },
      },
    ];

    render(
      <MemoryRouter>
        <ApplicantsTable applications={mockApplications} />
      </MemoryRouter>
    );

    expect(screen.getByText('Alex Developer')).toBeInTheDocument();
    expect(screen.getByText('Nairobi University')).toBeInTheDocument();
    expect(screen.getByText('Computer Science')).toBeInTheDocument();
    expect(screen.getByText('Year 4')).toBeInTheDocument();
    expect(screen.getByText('Submitted')).toBeInTheDocument();

    const reviewLink = screen.getByRole('link', { name: 'Review' });
    expect(reviewLink).toHaveAttribute('href', '/applications/101');
  });
});
