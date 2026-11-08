import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { StudyPlanPage } from './StudyPlanPage';
import { StudyPlanResponse } from '../types/study_plan';

const mockFullPlan: StudyPlanResponse = {
  generated_at: '2026-11-07T08:00:00Z',
  window: { days: 7, start_date: '2026-11-07', end_date: '2026-11-13' },
  summary: {
    headline: 'You have 2 coursework tasks scheduled across 7 days.',
    sentences: [
      'You are currently enrolled in 2 published courses.',
      '1 assignment is currently overdue and scheduled for immediate catch-up.',
      "Your nearest achievement milestone is 'Course finisher' (1 of 3 completed).",
    ],
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
          reason: 'Overdue assignment &bull; catch up first',
          flags: ['overdue'],
        },
      ],
    },
    {
      date: '2026-11-08',
      items: [
        {
          type: 'internship',
          title: 'Backend Software Engineering Intern',
          link_path: '/internships/401',
          due_at: '2026-11-08T23:59:59Z',
          suggested_minutes: 0,
          reason: 'Apply by 08 Nov 2026 (Complete your profile to apply)',
          flags: ['profile_incomplete'],
        },
      ],
    },
  ],
};

describe('StudyPlanPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading state and displays full study plan once loaded', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockFullPlan), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter>
        <StudyPlanPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('status')).toHaveTextContent(
      /Generating deterministic study schedule/i
    );

    await waitFor(() => {
      expect(screen.getByText('Study plan & weekly progress')).toBeInTheDocument();
      expect(screen.getByText(mockFullPlan.summary.headline)).toBeInTheDocument();
      expect(
        screen.getByText('1 assignment is currently overdue and scheduled for immediate catch-up.')
      ).toBeInTheDocument();
    });

    expect(screen.getByText('Lab 1: Shell Implementation')).toBeInTheDocument();
    expect(screen.getByText('Backend Software Engineering Intern')).toBeInTheDocument();
    expect(screen.getAllByText('Overdue').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Profile incomplete')).toBeInTheDocument();
    expect(screen.getByTestId('back-link')).toBeInTheDocument();
  });

  it('switches window length selector between 7 days and 14 days', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      const days = url.includes('days=14') ? 14 : 7;
      return new Response(
        JSON.stringify({ ...mockFullPlan, window: { ...mockFullPlan.window, days } }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    });

    render(
      <MemoryRouter initialEntries={['/study-plan']}>
        <StudyPlanPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('days-selector-7')).toHaveAttribute('aria-pressed', 'true');
    });

    fireEvent.click(screen.getByTestId('days-selector-14'));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining('days=14'), expect.anything());
    });
  });

  it('toggles "How this plan is made" disclosure and verifies rule-based descriptions without AI', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockFullPlan), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter>
        <StudyPlanPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('How this plan is made')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('study-plan-rules-content')).not.toBeInTheDocument();

    fireEvent.click(screen.getByText('How this plan is made'));

    const content = screen.getByTestId('study-plan-rules-content');
    expect(content).toBeInTheDocument();
    expect(content.textContent).toContain('deterministic');
    expect(content.textContent).toContain('120 minutes');
    expect(content.textContent).not.toMatch(/\bai\b/i);
    expect(content.textContent).not.toMatch(/artificial intelligence/i);
  });

  it('renders not enrolled empty state', async () => {
    const notEnrolledPlan: StudyPlanResponse = {
      ...mockFullPlan,
      summary: {
        ...mockFullPlan.summary,
        metrics: { ...mockFullPlan.summary.metrics, enrolled_courses_count: 0 },
      },
      plan: [],
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(notEnrolledPlan), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter>
        <StudyPlanPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Not enrolled in any course')).toBeInTheDocument();
      expect(screen.getByText('Browse course catalog')).toBeInTheDocument();
    });
  });

  it('renders schedule clear empty state when enrolled with 0 tasks', async () => {
    const clearPlan: StudyPlanResponse = {
      ...mockFullPlan,
      summary: {
        ...mockFullPlan.summary,
        metrics: {
          ...mockFullPlan.summary.metrics,
          enrolled_courses_count: 2,
          assignments_due_count: 0,
        },
      },
      plan: [{ date: '2026-11-07', items: [] }],
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(clearPlan), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter>
        <StudyPlanPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Schedule is clear')).toBeInTheDocument();
    });
  });

  it('renders error state and retries on click', async () => {
    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockRejectedValueOnce(new Error('Server unavailable'))
      .mockResolvedValueOnce(
        new Response(JSON.stringify(mockFullPlan), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      );

    render(
      <MemoryRouter>
        <StudyPlanPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Server unavailable')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /retry/i }));

    await waitFor(() => {
      expect(screen.getByText(mockFullPlan.summary.headline)).toBeInTheDocument();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });
});
