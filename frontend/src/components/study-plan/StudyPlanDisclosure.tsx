import React, { useState } from 'react';
import { ChevronDown, ChevronRight, HelpCircle } from 'lucide-react';

export const StudyPlanDisclosure: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section
      className="bg-surface border border-line rounded-control overflow-hidden"
      aria-label="How this plan is made"
    >
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="w-full p-4 flex items-center justify-between text-left hover:bg-chalk transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol"
      >
        <div className="flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-pencil shrink-0" aria-hidden="true" />
          <span className="text-sm font-semibold text-ink">How this plan is made</span>
          <span className="text-xs text-pencil border border-line px-1.5 py-0.5 rounded-sm">
            Rule-based plan
          </span>
        </div>
        {isOpen ? (
          <ChevronDown className="h-4 w-4 text-pencil shrink-0" aria-hidden="true" />
        ) : (
          <ChevronRight className="h-4 w-4 text-pencil shrink-0" aria-hidden="true" />
        )}
      </button>

      {isOpen && (
        <div
          data-testid="study-plan-rules-content"
          className="p-4 pt-0 border-t border-line text-xs sm:text-sm text-pencil space-y-2 bg-surface"
        >
          <p className="font-medium text-ink">
            This schedule is generated deterministically using transparent domain rules:
          </p>
          <ul className="list-disc pl-5 space-y-1.5">
            <li>
              <strong>Prioritization:</strong> Overdue assignments are scheduled first, followed by
              upcoming assignments ordered by earliest due date, largest point value, and ID.
            </li>
            <li>
              <strong>Effort estimation:</strong> Work is estimated by assignment points (45 mins
              for up to 20 pts, 90 mins for up to 50 pts, and 150 mins for over 50 pts).
            </li>
            <li>
              <strong>Daily workload cap:</strong> Each day has a maximum of 120 minutes of planned
              study. Preparation is scheduled as late as possible on days strictly before due dates.
            </li>
            <li>
              <strong>Tight schedule flag:</strong> If a task cannot fit in the remaining capacity
              before its due date, work begins immediately from today up through the due date and is
              labeled as tight.
            </li>
            <li>
              <strong>Exclusion:</strong> Assignments you have already submitted or received grades
              for are automatically excluded from the schedule.
            </li>
            <li>
              <strong>Internships:</strong> Suggested open internships with deadlines inside your
              chosen window are included alongside profile completion reminders.
            </li>
          </ul>
        </div>
      )}
    </section>
  );
};
