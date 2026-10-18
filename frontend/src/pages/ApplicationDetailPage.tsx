import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { decideApplication, getApplicationById } from '../api/application';
import { ApplicationStatusBadge } from '../components/internships/ApplicationStatusBadge';
import { DecisionForm } from '../components/internships/DecisionForm';
import { AppShell } from '../components/layout/AppShell';
import { Badge, ErrorMessage, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { formatDateTime } from '../lib/dates';
import { Application } from '../types/application';

export const ApplicationDetailPage: React.FC = () => {
  usePageTitle('Application review');
  const { id } = useParams<{ id: string }>();
  const applicationId = Number(id);
  const { user } = useAuth();

  const [application, setApplication] = useState<Application | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadApplication = useCallback(async () => {
    if (!applicationId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getApplicationById(applicationId);
      setApplication(data);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Failed to load application.');
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    loadApplication();
  }, [loadApplication]);

  const handleDecision = async (
    status: 'shortlisted' | 'accepted' | 'rejected',
    message?: string
  ) => {
    if (!application) return;
    setSubmitting(true);
    setError(null);
    try {
      await decideApplication(application.id, {
        status,
        decision_message: message,
      });
      await loadApplication();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Failed to submit decision.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="p-8 text-center text-pencil">Loading application...</div>
      </AppShell>
    );
  }

  if (!application) {
    return (
      <AppShell>
        <div className="p-8 text-center">
          <ErrorMessage
            whatHappened={error || 'Application not found.'}
            howToFix="Please try again or return to the application."
          />
        </div>
      </AppShell>
    );
  }

  const isOrg = user?.role === 'organization';
  const isFinal =
    application.status === 'accepted' ||
    application.status === 'rejected' ||
    application.status === 'withdrawn';

  const backLink =
    user?.role === 'student' ? '/my-applications' : `/internships/${application.posting_id}`;
  const backLabel = user?.role === 'student' ? 'my applications' : 'internship posting';

  return (
    <AppShell>
      <div className="space-y-6 max-w-3xl">
        <div>
          <Link
            to={backLink}
            className="text-sm text-petrol hover:underline font-medium mb-2 inline-block"
          >
            &larr; Back to {backLabel}
          </Link>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <PageHeader
              title={`Application #${application.id}`}
              description={application.posting_title || 'Internship posting'}
            />
            <ApplicationStatusBadge status={application.status} />
          </div>
        </div>

        {error && (
          <ErrorMessage
            whatHappened={error}
            howToFix="Please try again or return to the application."
          />
        )}

        {application.applicant && (
          <div className="bg-surface rounded-card p-5 border border-line space-y-4">
            <h2 className="text-base font-semibold text-ink">Applicant details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-pencil block">Full name</span>
                <span className="font-medium text-ink">{application.applicant.full_name}</span>
              </div>
              <div>
                <span className="text-pencil block">Email</span>
                <span className="text-ink">{application.applicant.email}</span>
              </div>
              <div>
                <span className="text-pencil block">University</span>
                <span className="text-ink">{application.applicant.university || '—'}</span>
              </div>
              <div>
                <span className="text-pencil block">Department</span>
                <span className="text-ink">{application.applicant.department || '—'}</span>
              </div>
              <div>
                <span className="text-pencil block">Year of study</span>
                <span className="text-ink">
                  {application.applicant.year_of_study
                    ? `Year ${application.applicant.year_of_study}`
                    : '—'}
                </span>
              </div>
            </div>

            {application.applicant.skills.length > 0 && (
              <div className="pt-2">
                <span className="text-pencil text-sm block mb-1.5">Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {application.applicant.skills.map((skill) => (
                    <Badge key={skill} variant="neutral">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {application.applicant.bio && (
              <div className="pt-2 border-t border-line text-sm">
                <span className="text-pencil block mb-1 font-medium">Bio</span>
                <p className="text-ink">{application.applicant.bio}</p>
              </div>
            )}
          </div>
        )}

        <div className="bg-surface rounded-card p-5 border border-line space-y-2">
          <h2 className="text-base font-semibold text-ink">Cover letter</h2>
          <p className="text-ink text-sm whitespace-pre-line leading-relaxed">
            {application.cover_letter}
          </p>
        </div>

        {isFinal && (
          <div className="bg-surface rounded-card p-5 border border-line space-y-2">
            <h2 className="text-base font-semibold text-ink">Decision status</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-ink">Decision:</span>
              <ApplicationStatusBadge status={application.status} />
              {application.decided_at && (
                <span className="text-xs text-pencil">
                  on {formatDateTime(application.decided_at)}
                </span>
              )}
            </div>
            {application.decision_message && (
              <p className="text-sm text-pencil pt-1 whitespace-pre-line">
                {application.decision_message}
              </p>
            )}
          </div>
        )}

        {isOrg && !isFinal && (
          <div className="bg-surface rounded-card p-5 border border-line space-y-3">
            <h2 className="text-base font-semibold text-ink">Make a decision</h2>
            <DecisionForm
              currentStatus={application.status}
              onSubmit={handleDecision}
              isSubmitting={submitting}
              error={error}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
};
