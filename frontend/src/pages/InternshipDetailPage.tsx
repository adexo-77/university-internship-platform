import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getInternshipById, updateInternship } from '../api/internship';
import {
  applyToInternship,
  getInternshipApplications,
  getStudentApplications,
  withdrawApplication,
} from '../api/application';
import { getStudentProfile } from '../api/profile';
import { DueBadge } from '../components/assignments/DueBadge';
import { InternshipApplicantsSection } from '../components/internships/InternshipApplicantsSection';
import { InternshipStatusBadge } from '../components/internships/InternshipStatusBadge';
import { StudentApplicationPanel } from '../components/internships/StudentApplicationPanel';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { Application } from '../types/application';
import { Internship } from '../types/internship';
import { StudentProfile } from '../types/profile';

export const InternshipDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const postingId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();

  const [internship, setInternship] = useState<Internship | null>(null);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [myApp, setMyApp] = useState<Application | null>(null);
  const [roster, setRoster] = useState<Application[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
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
        const match = myApps.find((a) => a.posting_id === postingId);
        setMyApp(match ?? null);
      } else if (user?.role === 'organization' || user?.role === 'admin') {
        const apps = await getInternshipApplications(postingId, statusFilter || undefined);
        setRoster(apps);
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Failed to load internship.');
    } finally {
      setLoading(false);
    }
  }, [postingId, user?.role, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApply = async (coverLetter: string) => {
    setSubmitting(true);
    setError(null);
    try {
      await applyToInternship(postingId, { cover_letter: coverLetter });
      await loadData();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Failed to submit application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWithdraw = async () => {
    if (!myApp) return;
    setSubmitting(true);
    setError(null);
    try {
      await withdrawApplication(myApp.id);
      await loadData();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Failed to withdraw application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePublish = async () => {
    if (!internship) return;
    if (!window.confirm('Publish this internship to make it open for applications?')) return;
    try {
      await updateInternship(internship.id, { status: 'open' });
      await loadData();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

  const handleClose = async () => {
    if (!internship) return;
    if (!window.confirm('Close this internship? Closed postings cannot be reopened.')) return;
    try {
      await updateInternship(internship.id, { status: 'closed' });
      await loadData();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
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
          <div className="flex items-center gap-2 flex-wrap">
            <InternshipStatusBadge status={internship.status} />
            {isOwner && internship.status !== 'closed' && (
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate(`/internships/${internship.id}/edit`)}
              >
                Edit
              </Button>
            )}
            {isOwner && internship.status === 'draft' && (
              <Button type="button" variant="primary" onClick={handlePublish}>
                Publish
              </Button>
            )}
            {isOwner && internship.status === 'open' && (
              <Button type="button" variant="danger" onClick={handleClose}>
                Close
              </Button>
            )}
          </div>
        </div>

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-surface rounded-card border border-line text-sm">
          <div>
            <span className="text-pencil block">Location</span>
            <span className="font-medium text-ink">{internship.location}</span>
          </div>
          <div>
            <span className="text-pencil block">Work mode</span>
            <span className="font-medium text-ink capitalize">{internship.work_mode}</span>
          </div>
          <div>
            <span className="text-pencil block">Duration</span>
            <span className="font-medium text-ink">
              {internship.duration_weeks ? `${internship.duration_weeks} weeks` : 'Flexible'}
            </span>
          </div>
          <div className="md:col-span-3">
            <span className="text-pencil block">Application deadline</span>
            <DueBadge dueAt={internship.application_deadline} />
          </div>
        </div>

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
            error={error}
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
