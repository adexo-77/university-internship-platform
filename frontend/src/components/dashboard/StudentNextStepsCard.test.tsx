import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { StudentNextStepsCard } from './StudentNextStepsCard';
import { StudyPlanResponse } from '../../types/study_plan';

const mockStudyPlan: StudyPlanResponse = {
  generated_at: '2026-11-07T08:00:00Z',
  window: { days: 7, start_date: '2026-11-07', end_date: '2026-11-13' },
  summary: {
    headline: 'You have 2 assignments due this week.',
    sentences: ['Complete your urgent assignments.'],
    metrics: {
      enrolled_courses_count: 2,
      assignments_due_count: 2,
      total_scheduled_minutes: 180,
      overdue_assignments_count: 1,
    },
  },
  plan: [
    {
      date: '2026-11-07',
      items: [
        {
          type: 'assignment',
          title: 'Lab 1: Shell Implementation',
          link_path: '/assignments/101',
          due_at: '2026-11-06T12:00:00Z',
          suggested_minutes: 90,
          reason: 'Overdue assignment',
          flags: ['overdue'],
        },
        {
          type: 'assignment',
          title: 'Quiz 2: Memory Management',
          link_path: '/assignments/102',
          due_at: '2026-11-08T12:00:00Z',
          suggested_minutes: 90,
          reason: 'Due tomorrow',
          flags: ['tight'],
        },
      ],
    },
  ],
};

describe('StudentNextStepsCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders top items with badges, links, and study plan link', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockStudyPlan), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter>
        <StudentNextStepsCard />
      </MemoryRouter>
    );

    expect(screen.getByRole('status')).toHaveTextContent('Loading next steps...');

    await waitFor(() => {
      expect(screen.getByText('Lab 1: Shell Implementation')).toBeInTheDocument();
      expect(screen.getByText('Quiz 2: Memory Management')).toBeInTheDocument();
    });

    expect(screen.getByText('Overdue')).toBeInTheDocument();
    expect(screen.getByText('Tight schedule')).toBeInTheDocument();
    expect(screen.getByText('Rule-based plan')).toBeInTheDocument();

    const fullPlanLink = screen.getByRole('link', { name: /Open full study plan/i });
    expect(fullPlanLink).toHaveAttribute('href', '/study-plan');
  });

  it('renders empty state when there are no pending tasks', async () => {
    const emptyPlan: StudyPlanResponse = {
      ...mockStudyPlan,
      plan: [{ date: '2026-11-07', items: [] }],
    };

    render(
      <MemoryRouter>
        <StudentNextStepsCard initialPlan={emptyPlan} />
      </MemoryRouter>
    );

    expect(
      screen.getByText(/No pending tasks scheduled. Your study plan is all caught up./i)
    ).toBeInTheDocument();
  });

  it('renders error state on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <StudentNextStepsCard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Network error');
    });
  });
});
