import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  closeInternship,
  getInternshipById,
  submitInternship,
  withdrawInternship,
} from '../api/internship';
import {
  applyToInternship,
  getInternshipApplications,
  getStudentApplications,
  withdrawApplication,
} from '../api/application';
import { getStudentProfile } from '../api/profile';
import { InternshipActionsBar } from '../components/internships/InternshipActionsBar';
import { InternshipApplicantsSection } from '../components/internships/InternshipApplicantsSection';
import { InternshipInfoCard } from '../components/internships/InternshipInfoCard';
import { StudentApplicationPanel } from '../components/internships/StudentApplicationPanel';
import { AppShell } from '../components/layout/AppShell';
import { ErrorMessage, Notice, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { Application } from '../types/application';
import { Internship } from '../types/internship';
import { StudentProfile } from '../types/profile';

export const InternshipDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const postingId = Number(id);
  const { user } = useAuth();

  const [internship, setInternship] = useState<Internship | null>(null);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [myApp, setMyApp] = useState<Application | null>(null);
  const [roster, setRoster] = useState<Application[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  usePageTitle(internship?.title ?? 'Internship details');

  const isOwner = user?.role === 'organization' && user?.id === internship?.organization_id;
  const isAdmin = user?.role === 'admin';
  const isStudent = user?.role === 'student';

  const loadData = useCallback(async () => {
    if (!postingId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getInternshipById(postingId);
      setInternship(data);
      if (user?.role === 'student') {
        const [profData, myApps] = await Promise.all([
          getStudentProfile().catch(() => null),
          getStudentApplications().catch(() => []),
        ]);
        setProfile(profData);
        setMyApp(myApps.find((a) => a.posting_id === postingId) ?? null);
      } else if (user?.role === 'organization' || user?.role === 'admin') {
        setRoster(await getInternshipApplications(postingId, statusFilter || undefined));
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load internship.');
    } finally {
      setLoading(false);
    }
  }, [postingId, user?.role, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApply = async (coverLetter: string) => {
    setSubmitting(true);
    setActionError(null);
    try {
      await applyToInternship(postingId, { cover_letter: coverLetter });
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to submit application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWithdraw = async () => {
    if (!myApp) return;
    setSubmitting(true);
    setActionError(null);
    try {
      await withdrawApplication(myApp.id);
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to withdraw application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!internship) return;
    setActionError(null);
    try {
      await submitInternship(internship.id);
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to submit for review.');
    }
  };

  const handleWithdrawToDraft = async () => {
    if (!internship) return;
    setActionError(null);
    try {
      await withdrawInternship(internship.id);
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to withdraw to draft.');
    }
  };

  const handleClose = async () => {
    if (!internship) return;
    if (!window.confirm('Close this internship? Closed postings cannot be reopened.')) return;
    setActionError(null);
    try {
      await closeInternship(internship.id);
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to close internship.');
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="p-8 text-center text-pencil">Loading details...</div>
      </AppShell>
    );
  }

  if (!internship) {
    return (
      <AppShell>
        <div className="p-8 text-center">
          <ErrorMessage
            whatHappened={error || 'Internship not found.'}
            howToFix="Please try again or return to the internships catalogue."
          />
        </div>
      </AppShell>
    );
  }

  const isProfileComplete = Boolean(
    profile && profile.university?.trim() && profile.department?.trim()
  );

  return (
    <AppShell>
      <div className="space-y-6 max-w-4xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <PageHeader
            title={internship.title}
            description={internship.organization_name ?? 'Organization'}
          />
          <InternshipActionsBar
            internship={internship}
            isOwner={Boolean(isOwner)}
            onSubmitForReview={handleSubmitForReview}
            onWithdrawToDraft={handleWithdrawToDraft}
            onClose={handleClose}
          />
        </div>

        {actionError && (
          <ErrorMessage
            whatHappened={actionError}
            howToFix="Review requirements or contact support if the issue persists."
          />
        )}

        {internship.status === 'rejected' && internship.review_note && (
          <Notice variant="error" title="Review note">
            <p className="whitespace-pre-line">{internship.review_note}</p>
            {isOwner && (
              <p className="mt-2">
                <Link
                  to={`/internships/${internship.id}/edit`}
                  className="font-semibold text-petrol underline"
                >
                  Edit posting to address feedback
                </Link>
              </p>
            )}
          </Notice>
        )}

        <InternshipInfoCard internship={internship} />

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-ink">Description</h2>
          <p className="text-ink whitespace-pre-line leading-relaxed">{internship.description}</p>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-ink">Requirements</h2>
          <p className="text-ink whitespace-pre-line leading-relaxed">{internship.requirements}</p>
        </div>

        {isStudent && (
          <StudentApplicationPanel
            internship={internship}
            myApp={myApp}
            isProfileComplete={isProfileComplete}
            submitting={submitting}
            error={actionError}
            onApply={handleApply}
            onWithdraw={handleWithdraw}
          />
        )}

        {(isOwner || isAdmin) && (
          <InternshipApplicantsSection
            roster={roster}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
          />
        )}
      </div>
    </AppShell>
  );
};
