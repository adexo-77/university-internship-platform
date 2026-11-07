import React, { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getStudentStudyPlan } from '../api/study_plan';
import { StudyPlanDisclosure } from '../components/study-plan/StudyPlanDisclosure';
import { StudyPlanSchedule } from '../components/study-plan/StudyPlanSchedule';
import { StudyPlanSummaryCard } from '../components/study-plan/StudyPlanSummaryCard';
import { BackLink, Button, EmptyState, ErrorMessage, PageHeader, TextLink } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { StudyPlanResponse } from '../types/study_plan';

export const StudyPlanPage: React.FC = () => {
  usePageTitle('Study plan');
  const [searchParams, setSearchParams] = useSearchParams();

  const daysParam = parseInt(searchParams.get('days') || '7', 10);
  const selectedDays = daysParam === 14 ? 14 : 7;

  const [data, setData] = useState<StudyPlanResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = useCallback(async (days: number) => {
    setLoading(true);
    setError(null);
    try {
      const plan = await getStudentStudyPlan(days);
      setData(plan);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load study plan.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlan(selectedDays);
  }, [fetchPlan, selectedDays]);

  const handleDaysChange = (newDays: number): void => {
    setSearchParams({ days: String(newDays) });
  };

  const totalItems = data ? data.plan.reduce((sum, d) => sum + d.items.length, 0) : 0;
  const enrolledCourses = data?.summary.metrics.enrolled_courses_count ?? 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto px-4 sm:px-6 py-6 overflow-x-hidden">
      <BackLink />

      <PageHeader
        title="Study plan & weekly progress"
        description="A deterministic rule-based schedule prioritizing pending coursework and upcoming opportunities."
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface p-3 border border-line rounded-control">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-pencil">
            Window:
          </span>
          <div
            className="inline-flex rounded-control border border-line p-0.5 bg-chalk/60"
            role="group"
            aria-label="Window length selector"
          >
            <button
              type="button"
              onClick={() => handleDaysChange(7)}
              data-testid="days-selector-7"
              aria-pressed={selectedDays === 7}
              className={`px-3 py-1 text-xs font-medium rounded-control transition-colors ${
                selectedDays === 7
                  ? 'bg-surface text-ink shadow-xs border border-line'
                  : 'text-pencil hover:text-ink'
              }`}
            >
              7 days
            </button>
            <button
              type="button"
              onClick={() => handleDaysChange(14)}
              data-testid="days-selector-14"
              aria-pressed={selectedDays === 14}
              className={`px-3 py-1 text-xs font-medium rounded-control transition-colors ${
                selectedDays === 14
                  ? 'bg-surface text-ink shadow-xs border border-line'
                  : 'text-pencil hover:text-ink'
              }`}
            >
              14 days
            </button>
          </div>
        </div>

        <span className="text-xs text-pencil border border-line px-2 py-0.5 rounded-sm self-start sm:self-auto">
          Rule-based plan &bull; No AI
        </span>
      </div>

      {loading && (
        <div className="p-8 text-center text-sm text-pencil" role="status">
          Generating deterministic study schedule...
        </div>
      )}

      {error && !loading && (
        <div className="space-y-3">
          <ErrorMessage whatHappened="Failed to load study plan." howToFix={error} />
          <Button variant="secondary" onClick={() => fetchPlan(selectedDays)}>
            Retry
          </Button>
        </div>
      )}

      {!loading && !error && data && (
        <div className="space-y-6">
          <StudyPlanSummaryCard summary={data.summary} />

          {enrolledCourses === 0 ? (
            <EmptyState
              title="Not enrolled in any course"
              description="Enroll in published courses to generate your personalized coursework schedule."
              action={
                <TextLink to="/courses" variant="primary">
                  Browse course catalog
                </TextLink>
              }
            />
          ) : totalItems === 0 ? (
            <EmptyState
              title="Schedule is clear"
              description="You have no pending assignments or application deadlines in this window."
              action={
                <TextLink to="/courses" variant="subtle">
                  View enrolled courses
                </TextLink>
              }
            />
          ) : (
            <StudyPlanSchedule days={data.plan} />
          )}

          <StudyPlanDisclosure />
        </div>
      )}
    </div>
  );
};
