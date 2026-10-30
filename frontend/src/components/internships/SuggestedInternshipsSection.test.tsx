import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { SuggestedInternshipsSection } from './SuggestedInternshipsSection';
import { InternshipSuggestionResponse } from '../../types/internship';

const mockSuggestionsData: InternshipSuggestionResponse = {
  items: [
    {
      id: 101,
      organization_id: 1,
      organization_name: 'Acme Corp',
      title: 'Backend Python Intern',
      description: 'Work with Python and FastAPI.',
      requirements: 'Python skills required.',
      location: 'Addis Ababa',
      work_mode: 'remote',
      application_deadline: '2026-11-15T00:00:00Z',
      status: 'open',
      created_at: '2026-10-20T00:00:00Z',
      updated_at: '2026-10-20T00:00:00Z',
      score: 72,
      reasons: {
        matched_skills: ['Python', 'FastAPI'],
        work_mode_match: true,
        location_match: true,
      },
    },
  ],
  reason_code: null,
};

describe('SuggestedInternshipsSection Component', () => {
  it('renders section title, rule-based label, and matching internship cards', () => {
    render(
      <MemoryRouter>
        <SuggestedInternshipsSection initialData={mockSuggestionsData} />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: 'Suggested for you' })).toBeInTheDocument();
    expect(screen.getByText('Rule-based suggestions')).toBeInTheDocument();

    // Check card details
    expect(screen.getByRole('link', { name: 'Backend Python Intern' })).toBeInTheDocument();
    expect(screen.getByText(/Acme Corp/)).toBeInTheDocument();
    expect(screen.getByText('72% match')).toBeInTheDocument();
    expect(screen.getByText('Skills:')).toBeInTheDocument();
    expect(screen.getByText(/Python, FastAPI/)).toBeInTheDocument();
    expect(screen.getByText(/Work mode matches preference/)).toBeInTheDocument();
    expect(screen.getByText(/Location: Remote/)).toBeInTheDocument();
  });

  it('toggles "How matching works" explanatory note with weights', () => {
    render(
      <MemoryRouter>
        <SuggestedInternshipsSection initialData={mockSuggestionsData} />
      </MemoryRouter>
    );

    expect(screen.queryByTestId('how-matching-works-note')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /How matching works/i }));
    expect(screen.getByTestId('how-matching-works-note')).toBeInTheDocument();
    expect(screen.getByTestId('how-matching-works-note')).toHaveTextContent('60 points for skills');
    expect(screen.getByTestId('how-matching-works-note')).toHaveTextContent('20 points');
  });

  it('renders empty state when student has no skills with link to Profile', () => {
    const noSkillsData: InternshipSuggestionResponse = {
      items: [],
      reason_code: 'NO_SKILLS',
    };

    render(
      <MemoryRouter>
        <SuggestedInternshipsSection initialData={noSkillsData} />
      </MemoryRouter>
    );

    expect(screen.getByText('No skills on your profile yet')).toBeInTheDocument();
    const profileLink = screen.getByRole('link', { name: 'Go to Profile' });
    expect(profileLink).toBeInTheDocument();
    expect(profileLink).toHaveAttribute('href', '/profile');
  });

  it('renders empty state when student has skills but nothing matches', () => {
    const noMatchesData: InternshipSuggestionResponse = {
      items: [],
      reason_code: null,
    };

    render(
      <MemoryRouter>
        <SuggestedInternshipsSection initialData={noMatchesData} />
      </MemoryRouter>
    );

    expect(screen.getByText('No matching suggestions right now')).toBeInTheDocument();
  });

  it('renders compact mode with browse all link', () => {
    render(
      <MemoryRouter>
        <SuggestedInternshipsSection compact initialData={mockSuggestionsData} />
      </MemoryRouter>
    );

    expect(screen.getByRole('link', { name: /Browse all internships/i })).toBeInTheDocument();
  });
});
