import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getStudentStudyPlan } from '../../api/study_plan';
import { StudyPlanItem, StudyPlanResponse } from '../../types/study_plan';
import { Badge } from '../ui/Badge';
import { formatDate } from '../../lib/dates';

export interface StudentNextStepsCardProps {
  initialPlan?: StudyPlanResponse;
}

export const StudentNextStepsCard: React.FC<StudentNextStepsCardProps> = ({ initialPlan }) => {
  const [plan, setPlan] = useState<StudyPlanResponse | null>(initialPlan ?? null);
  const [loading, setLoading] = useState<boolean>(!initialPlan);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialPlan) {
      setPlan(initialPlan);
      setLoading(false);
      return;
    }

    let isMounted = true;
    getStudentStudyPlan(7)
      .then((data) => {
        if (isMounted) {
          setPlan(data);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load study plan.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [initialPlan]);

  // Extract top 3 pending or tight items across the window
  const allItems: StudyPlanItem[] = Array.isArray(plan?.plan)
    ? plan.plan.flatMap((day) => (Array.isArray(day?.items) ? day.items : []))
    : [];

  const topItems = [...allItems]
    .sort((a, b) => {
      const aPriority = a.flags.includes('overdue') ? 2 : a.flags.includes('tight') ? 1 : 0;
      const bPriority = b.flags.includes('overdue') ? 2 : b.flags.includes('tight') ? 1 : 0;
      if (bPriority !== aPriority) {
        return bPriority - aPriority;
      }
      return new Date(a.due_at).getTime() - new Date(b.due_at).getTime();
    })
    .slice(0, 3);

  return (
    <section className="space-y-3" aria-labelledby="next-steps-heading">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 id="next-steps-heading" className="text-base font-semibold text-ink">
            Next steps
          </h2>
          <span className="text-xs text-pencil border border-line px-1.5 py-0.5 rounded-sm">
            Rule-based plan
          </span>
        </div>
        <Link
          to="/study-plan"
          className="text-xs sm:text-sm font-medium text-petrol hover:text-petrol-hover underline underline-offset-2"
        >
          Open full study plan &rarr;
        </Link>
      </div>

      <div className="bg-surface border border-line rounded-control overflow-hidden">
        {loading ? (
          <div className="p-4 text-sm text-pencil" role="status">
            Loading next steps...
          </div>
        ) : error ? (
          <div className="p-4 text-sm text-brick" role="alert">
            {error}
          </div>
        ) : topItems.length === 0 ? (
          <div className="p-4 text-sm text-pencil">
            No pending tasks scheduled. Your study plan is all caught up.
          </div>
        ) : (
          <ul className="divide-y divide-line" data-testid="next-steps-list">
            {topItems.map((item, index) => {
              const isOverdue = item.flags.includes('overdue');
              const isTight = item.flags.includes('tight');

              return (
                <li
                  key={`${item.type}-${item.title}-${index}`}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="neutral">
                        {item.type === 'assignment' ? 'Assignment' : 'Internship'}
                      </Badge>
                      {isOverdue && <Badge variant="error">Overdue</Badge>}
                      {isTight && <Badge variant="attention">Tight schedule</Badge>}
                      <Link
                        to={item.link_path}
                        className="font-medium text-ink hover:text-petrol transition-colors text-sm"
                      >
                        {item.title}
                      </Link>
                    </div>
                    <p className="text-xs text-pencil">
                      Due {formatDate(item.due_at)} &bull;{' '}
                      {item.suggested_minutes > 0
                        ? `${item.suggested_minutes} mins estimated`
                        : item.reason}
                    </p>
                  </div>
                  <Link
                    to={item.link_path}
                    className="text-xs font-medium text-petrol hover:text-petrol-hover underline shrink-0 self-start sm:self-auto"
                  >
                    View
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
};
