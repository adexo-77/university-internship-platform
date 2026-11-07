import React from 'react';
import { StudyPlanDay } from '../../types/study_plan';
import { Badge } from '../ui/Badge';
import { TextLink } from '../ui/TextLink';
import { formatDate } from '../../lib/dates';

export interface StudyPlanScheduleProps {
  days: StudyPlanDay[];
}

export const StudyPlanSchedule: React.FC<StudyPlanScheduleProps> = ({ days }) => {
  return (
    <div className="space-y-4" data-testid="study-plan-schedule">
      <h2 className="text-base font-semibold text-ink">Schedule by day</h2>
      <div className="space-y-4">
        {days.map((day) => {
          const totalDayMinutes = day.items.reduce((acc, i) => acc + i.suggested_minutes, 0);

          return (
            <div
              key={day.date}
              className="bg-surface border border-line rounded-control overflow-hidden"
              data-testid={`study-plan-day-${day.date}`}
            >
              <div className="bg-chalk/60 px-4 py-2.5 border-b border-line flex items-center justify-between flex-wrap gap-2">
                <span className="text-sm font-semibold text-ink">{formatDate(day.date)}</span>
                <span className="text-xs text-pencil font-medium tabular-nums">
                  {totalDayMinutes > 0
                    ? `${totalDayMinutes} mins scheduled`
                    : 'Rest or catch-up day'}
                </span>
              </div>

              {day.items.length === 0 ? (
                <div className="p-4 text-xs sm:text-sm text-pencil">
                  No tasks scheduled for this day.
                </div>
              ) : (
                <ul className="divide-y divide-line">
                  {day.items.map((item, idx) => {
                    const isOverdue = item.flags.includes('overdue');
                    const isTight = item.flags.includes('tight');
                    const isIncomplete = item.flags.includes('profile_incomplete');

                    return (
                      <li
                        key={`${item.type}-${item.title}-${idx}`}
                        className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-chalk/40 transition-colors"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge variant="neutral">
                              {item.type === 'assignment' ? 'Assignment' : 'Internship'}
                            </Badge>
                            {isOverdue && <Badge variant="error">Overdue</Badge>}
                            {isTight && <Badge variant="attention">Tight schedule</Badge>}
                            {isIncomplete && <Badge variant="attention">Profile incomplete</Badge>}
                            <TextLink to={item.link_path} className="text-sm font-medium">
                              {item.title}
                            </TextLink>
                          </div>
                          <p className="text-xs text-pencil">
                            Due {formatDate(item.due_at)} &bull; {item.reason}
                          </p>
                        </div>
                        <div className="text-left sm:text-right shrink-0">
                          {item.suggested_minutes > 0 ? (
                            <span className="text-xs font-semibold text-ink bg-chalk px-2 py-1 rounded-sm border border-line/60 tabular-nums">
                              {item.suggested_minutes} mins
                            </span>
                          ) : (
                            <TextLink to={item.link_path} variant="subtle" className="text-xs">
                              View details
                            </TextLink>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
