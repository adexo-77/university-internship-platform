import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as badgeApi from '../../api/badge';
import { AchievementBadge } from '../../types/badge';
import { StudentBadgesSection } from './StudentBadgesSection';

vi.mock('../../api/badge');

const mockBadges: AchievementBadge[] = [
  {
    id: 'first_submission',
    title: 'First submission',
    description: 'Submit your first course assignment.',
    earned: true,
  },
  {
    id: 'ontime_habit',
    title: 'On-time habit',
    description: 'Submit 5 assignments on or before the due date.',
    earned: false,
    progress: { current: 3, target: 5 },
  },
  {
    id: 'course_finisher',
    title: 'Course finisher',
    description: 'Submit every assignment in at least one course.',
    earned: false,
  },
];

describe('StudentBadgesSection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders earned and unearned badges with progress from props', () => {
    render(<StudentBadgesSection badges={mockBadges} />);

    expect(screen.getByText('Achievements & Badges')).toBeInTheDocument();
    expect(screen.getByText('1 of 3 earned')).toBeInTheDocument();

    expect(screen.getByText('First submission')).toBeInTheDocument();
    expect(screen.getByText('Earned')).toBeInTheDocument();

    expect(screen.getByText('On-time habit')).toBeInTheDocument();
    const progress = screen.getByTestId('progress-ontime_habit');
    expect(progress).toHaveTextContent('3 of 5');

    expect(screen.getByText('Course finisher')).toBeInTheDocument();
    expect(screen.getByText('Locked')).toBeInTheDocument();
  });

  it('renders empty state when no badges are available', () => {
    render(<StudentBadgesSection badges={[]} />);

    expect(screen.getByText('No badges available')).toBeInTheDocument();
    expect(
      screen.getByText('Achievement milestones and badges will appear here.')
    ).toBeInTheDocument();
  });

  it('fetches badges on mount when initialBadges is omitted', async () => {
    vi.mocked(badgeApi.getStudentBadges).mockResolvedValueOnce(mockBadges);

    render(<StudentBadgesSection />);

    expect(screen.getByText('Loading achievement badges...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('First submission')).toBeInTheDocument();
    });

    expect(badgeApi.getStudentBadges).toHaveBeenCalledTimes(1);
    expect(screen.getByText('1 of 3 earned')).toBeInTheDocument();
  });
});
