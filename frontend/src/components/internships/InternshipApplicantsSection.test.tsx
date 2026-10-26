import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { InternshipApplicantsSection } from './InternshipApplicantsSection';

describe('InternshipApplicantsSection', () => {
  it('renders heading and export CSV link when postingId is present', () => {
    const handleFilter = vi.fn();
    render(
      <MemoryRouter>
        <InternshipApplicantsSection
          postingId={12}
          roster={[]}
          statusFilter=""
          onStatusFilterChange={handleFilter}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Applicants (0)')).toBeInTheDocument();
    const exportLink = screen.getByRole('link', { name: 'Export CSV' });
    expect(exportLink).toBeInTheDocument();
    expect(exportLink).toHaveAttribute('href', '/api/internships/12/applicants.csv');
    expect(exportLink).toHaveAttribute('download', 'internship_12_applicants.csv');
  });

  it('omits export CSV link when postingId is undefined', () => {
    const handleFilter = vi.fn();
    render(
      <MemoryRouter>
        <InternshipApplicantsSection
          roster={[]}
          statusFilter=""
          onStatusFilterChange={handleFilter}
        />
      </MemoryRouter>
    );

    expect(screen.queryByRole('link', { name: 'Export CSV' })).not.toBeInTheDocument();
  });
});
