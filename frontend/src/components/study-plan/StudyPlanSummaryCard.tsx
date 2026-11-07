import React from 'react';
import { StudyPlanSummary } from '../../types/study_plan';

export interface StudyPlanSummaryCardProps {
  summary: StudyPlanSummary;
}

export const StudyPlanSummaryCard: React.FC<StudyPlanSummaryCardProps> = ({ summary }) => {
  const { headline, sentences, metrics } = summary;

  return (
    <div
      className="bg-surface border border-line rounded-control p-5 space-y-4 shadow-sm"
      data-testid="study-plan-summary-card"
    >
      <div className="space-y-1">
        <div className="flex items-center gap-2 flex-wrap">
          <h2 className="text-lg font-semibold text-ink">{headline}</h2>
          <span className="text-xs text-pencil border border-line px-2 py-0.5 rounded-sm">
            Rule-based plan
          </span>
        </div>
        <div className="space-y-1 pt-1 text-sm text-pencil">
          {sentences.map((sentence, idx) => (
            <p key={idx} className="leading-relaxed">
              {sentence}
            </p>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-line">
        <div className="bg-chalk/50 p-3 rounded-control border border-line/60">
          <p className="text-xs text-pencil font-medium">Courses</p>
          <p className="text-xl font-bold text-ink tabular-nums mt-0.5">
            {metrics.enrolled_courses_count}
          </p>
        </div>
        <div className="bg-chalk/50 p-3 rounded-control border border-line/60">
          <p className="text-xs text-pencil font-medium">Pending tasks</p>
          <p className="text-xl font-bold text-ink tabular-nums mt-0.5">
            {metrics.assignments_due_count}
          </p>
        </div>
        <div className="bg-chalk/50 p-3 rounded-control border border-line/60">
          <p className="text-xs text-pencil font-medium">Minutes planned</p>
          <p className="text-xl font-bold text-ink tabular-nums mt-0.5">
            {metrics.total_scheduled_minutes}
          </p>
        </div>
        <div className="bg-chalk/50 p-3 rounded-control border border-line/60">
          <p className="text-xs text-pencil font-medium">Overdue</p>
          <p
            className={`text-xl font-bold tabular-nums mt-0.5 ${
              metrics.overdue_assignments_count > 0 ? 'text-brick' : 'text-ink'
            }`}
          >
            {metrics.overdue_assignments_count}
          </p>
        </div>
      </div>
    </div>
  );
};
