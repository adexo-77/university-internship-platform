import React, { useEffect, useState } from 'react';
import { Award, Check } from 'lucide-react';
import { getStudentBadges } from '../../api/badge';
import { AchievementBadge } from '../../types/badge';
import { EmptyState } from '../ui';

export interface StudentBadgesSectionProps {
  badges?: AchievementBadge[];
}

export const StudentBadgesSection: React.FC<StudentBadgesSectionProps> = ({
  badges: initialBadges,
}) => {
  const [badges, setBadges] = useState<AchievementBadge[] | null>(
    Array.isArray(initialBadges) ? initialBadges : null
  );
  const [loading, setLoading] = useState<boolean>(!initialBadges);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialBadges) {
      setBadges(Array.isArray(initialBadges) ? initialBadges : []);
      setLoading(false);
      return;
    }

    let isMounted = true;
    getStudentBadges()
      .then((data) => {
        if (isMounted) {
          setBadges(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load badges.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [initialBadges]);

  if (loading) {
    return (
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-ink">Achievements & Badges</h2>
        <div className="py-6 text-center text-sm text-pencil">Loading achievement badges...</div>
      </section>
    );
  }

  if (error || !Array.isArray(badges)) {
    return null;
  }

  const earnedCount = badges.filter((b) => b.earned).length;

  return (
    <section className="space-y-3" aria-labelledby="achievements-heading">
      <div className="flex items-center justify-between">
        <h2 id="achievements-heading" className="text-base font-semibold text-ink">
          Achievements & Badges
        </h2>
        <span className="text-xs text-pencil font-medium">
          {earnedCount} of {badges.length} earned
        </span>
      </div>

      {badges.length === 0 ? (
        <EmptyState
          title="No badges available"
          description="Achievement milestones and badges will appear here."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {badges.map((badge) => {
            const isEarned = badge.earned;
            return (
              <div
                key={badge.id}
                data-testid={`badge-card-${badge.id}`}
                className={`p-4 rounded-control border flex flex-col justify-between transition-colors ${
                  isEarned
                    ? 'border-line bg-surface shadow-none'
                    : 'border-line bg-chalk/60 opacity-80'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isEarned ? 'bg-petrol text-surface' : 'bg-line text-pencil'
                      }`}
                    >
                      {isEarned ? <Check className="w-4 h-4" /> : <Award className="w-4 h-4" />}
                    </div>
                    {isEarned ? (
                      <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-badge bg-petrol text-surface">
                        Earned
                      </span>
                    ) : badge.progress ? (
                      <span
                        className="text-xs font-semibold text-pencil tabular-nums"
                        data-testid={`progress-${badge.id}`}
                      >
                        {badge.progress.current} of {badge.progress.target}
                      </span>
                    ) : (
                      <span className="text-xs text-pencil">Locked</span>
                    )}
                  </div>
                  <div>
                    <h3
                      className={`text-sm font-semibold ${isEarned ? 'text-ink' : 'text-pencil'}`}
                    >
                      {badge.title}
                    </h3>
                    <p className="text-xs text-pencil mt-1 leading-relaxed">{badge.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
