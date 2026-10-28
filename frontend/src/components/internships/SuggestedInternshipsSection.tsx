import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, HelpCircle } from 'lucide-react';
import { getInternshipSuggestions } from '../../api/internship';
import { InternshipSuggestionItem, InternshipSuggestionResponse } from '../../types/internship';
import { Badge, EmptyState } from '../ui';

export interface SuggestedInternshipsSectionProps {
  limit?: number;
  compact?: boolean;
  initialData?: InternshipSuggestionResponse;
}

export const SuggestedInternshipsSection: React.FC<SuggestedInternshipsSectionProps> = ({
  limit = 5,
  compact = false,
  initialData,
}) => {
  const [data, setData] = useState<InternshipSuggestionResponse | null>(initialData ?? null);
  const [loading, setLoading] = useState<boolean>(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [showHowItWorks, setShowHowItWorks] = useState<boolean>(false);

  useEffect(() => {
    if (initialData) {
      setData(initialData);
      setLoading(false);
      return;
    }

    let isMounted = true;
    getInternshipSuggestions(limit)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load suggestions.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [limit, initialData]);

  if (loading) {
    return (
      <section className="space-y-3" aria-label="Suggested for you">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold text-ink">Suggested for you</h2>
          <Badge variant="neutral">Rule-based suggestions</Badge>
        </div>
        <div className="p-6 text-center text-sm text-pencil bg-surface border border-line rounded-control">
          Finding matching internships...
        </div>
      </section>
    );
  }

  if (error || !data) {
    return null;
  }

  return (
    <section
      className="space-y-3 bg-surface border border-line rounded-control p-4 shadow-sm"
      aria-label="Suggested for you"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-petrol font-semibold">
            <Sparkles className="w-4 h-4" />
            <h2 className="text-base text-ink font-semibold">Suggested for you</h2>
          </div>
          <Badge variant="neutral">Rule-based suggestions</Badge>
        </div>
        <button
          type="button"
          onClick={() => setShowHowItWorks((prev) => !prev)}
          className="text-xs text-pencil hover:text-ink flex items-center gap-1 self-start sm:self-auto transition-colors"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>How matching works</span>
        </button>
      </div>

      {showHowItWorks && (
        <div
          data-testid="how-matching-works-note"
          className="p-3 bg-canvas border border-line rounded-control text-xs text-pencil space-y-1"
        >
          <p className="font-medium text-ink">How matching works:</p>
          <p>
            Up to 60 points for skills (12 pts per matched skill, up to 5 skills), up to 20 points
            for preferred work mode (10 pts if no preference set), and up to 20 points for preferred
            location or remote work (10 pts if no preference set). Postings require at least 30
            points and 1 matching skill.
          </p>
        </div>
      )}

      {data.reason_code === 'NO_SKILLS' ? (
        <EmptyState
          title="No skills on your profile yet"
          description="Add your technical and academic skills to receive personalized rule-based internship suggestions."
          action={
            <Link
              to="/profile"
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-petrol text-surface border-petrol hover:bg-petrol-hover"
            >
              Go to Profile
            </Link>
          }
        />
      ) : data.items.length === 0 ? (
        <EmptyState
          title="No matching suggestions right now"
          description="No open internship postings currently match your skills and preferences. Check back later as new positions are added."
        />
      ) : (
        <div
          className={`grid gap-3 ${
            compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          }`}
        >
          {data.items.map((item) => (
            <SuggestionCard key={item.id} item={item} />
          ))}
        </div>
      )}

      {compact && data.items.length > 0 && (
        <div className="pt-2 text-right">
          <Link to="/internships" className="text-xs font-medium text-petrol hover:underline">
            Browse all internships &rarr;
          </Link>
        </div>
      )}
    </section>
  );
};

const SuggestionCard: React.FC<{ item: InternshipSuggestionItem }> = ({ item }) => {
  const reasons = item.reasons ?? {
    matched_skills: [],
    work_mode_match: null,
    location_match: null,
  };
  const matchedSkills = reasons.matched_skills ?? [];

  const getWorkModeText = (): string => {
    if (reasons.work_mode_match === true) {
      return `Work mode matches preference (${item.work_mode})`;
    }
    if (reasons.work_mode_match === false) {
      return `Work mode: ${item.work_mode}`;
    }
    return `Work mode: ${item.work_mode} (no preference)`;
  };

  const getLocationText = (): string => {
    if (item.work_mode === 'remote') {
      return 'Location: Remote (anywhere)';
    }
    if (reasons.location_match === true) {
      return `Location matches preference (${item.location})`;
    }
    if (reasons.location_match === false) {
      return `Location: ${item.location}`;
    }
    return `Location: ${item.location} (no preference)`;
  };

  return (
    <div
      data-testid={`suggestion-card-${item.id}`}
      className="p-3.5 bg-surface border border-line rounded-control hover:border-petrol transition-colors flex flex-col justify-between gap-2.5"
    >
      <div className="space-y-1">
        <div className="flex items-start justify-between gap-2">
          <Link
            to={`/internships/${item.id}`}
            className="font-medium text-sm text-ink hover:text-petrol transition-colors line-clamp-1"
          >
            {item.title}
          </Link>
          <span className="text-xs font-semibold text-petrol whitespace-nowrap tabular-nums">
            {item.score}% match
          </span>
        </div>
        <p className="text-xs text-pencil line-clamp-1">
          {item.organization_name || 'Organization'} &bull; {item.location}
        </p>
      </div>

      <div className="text-xs text-pencil border-t border-line/60 pt-2 space-y-1">
        {matchedSkills.length > 0 && (
          <p className="line-clamp-1">
            <span className="font-medium text-ink">Skills:</span> {matchedSkills.join(', ')}
          </p>
        )}
        <p className="line-clamp-1">{getWorkModeText()}</p>
        <p className="line-clamp-1">{getLocationText()}</p>
      </div>
    </div>
  );
};
