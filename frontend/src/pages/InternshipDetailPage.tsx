import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getInternshipById } from '../api/internship';
import { reviewInternship } from '../api/admin_internship';
import { getInternshipApplications, getStudentApplications } from '../api/application';
import { getStudentProfile } from '../api/profile';
import { AdminInternshipReviewModal } from '../components/admin/AdminInternshipReviewModal';
import { InternshipActionsBar } from '../components/internships/InternshipActionsBar';
import { InternshipApplicantsSection } from '../components/internships/InternshipApplicantsSection';
import { InternshipBodySections } from '../components/internships/InternshipBodySections';
import { InternshipInfoCard } from '../components/internships/InternshipInfoCard';
import { InternshipReviewNotice } from '../components/internships/InternshipReviewNotice';
import { StudentApplicationPanel } from '../components/internships/StudentApplicationPanel';
import { AppShell } from '../components/layout/AppShell';
import { ConfirmModal, ErrorMessage, PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { useInternshipActions } from '../hooks/useInternshipActions';
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
  const [error, setError] = useState<string | null>(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [isCloseModalOpen, setIsCloseModalOpen] = useState(false);

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

  const {
    submitting,
    actionError,
    handleApply,
    handleWithdraw,
    handleSubmitForReview,
    handleWithdrawToDraft,
    handleClose,
  } = useInternshipActions(internship, postingId, loadData);

  const handleAdminTakedown = async (decision: 'approved' | 'rejected', reviewNote?: string) => {
    if (!internship) return;
    setModalSubmitting(true);
    setModalError(null);
    try {
      const updated = await reviewInternship(internship.id, { decision, review_note: reviewNote });
      setInternship(updated);
      setIsReviewModalOpen(false);
    } catch (err: unknown) {
      setModalError(err instanceof Error ? err.message : 'Failed to take down posting.');
    } finally {
      setModalSubmitting(false);
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

  const isProfileComplete = Boolean(profile?.university?.trim() && profile?.department?.trim());

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
            isAdmin={Boolean(isAdmin)}
            onSubmitForReview={handleSubmitForReview}
            onWithdrawToDraft={handleWithdrawToDraft}
            onClose={() => setIsCloseModalOpen(true)}
            onTakeDown={() => {
              setModalError(null);
              setIsReviewModalOpen(true);
            }}
          />
        </div>

        {actionError && (
          <ErrorMessage
            whatHappened={actionError}
            howToFix="Review requirements or contact support if the issue persists."
          />
        )}

        <InternshipReviewNotice
          status={internship.status}
          reviewNote={internship.review_note}
          isOwner={Boolean(isOwner)}
          internshipId={internship.id}
        />
        <InternshipInfoCard internship={internship} />
        <InternshipBodySections
          description={internship.description}
          requirements={internship.requirements}
        />

        {isStudent && (
          <StudentApplicationPanel
            internship={internship}
            myApp={myApp}
            isProfileComplete={isProfileComplete}
            submitting={submitting}
            error={actionError}
            onApply={handleApply}
            onWithdraw={() => handleWithdraw(myApp?.id)}
          />
        )}

        {(isOwner || isAdmin) && (
          <InternshipApplicantsSection
            roster={roster}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
          />
        )}

        <AdminInternshipReviewModal
          internship={internship}
          isOpen={isReviewModalOpen}
          onClose={() => {
            setIsReviewModalOpen(false);
            setModalError(null);
          }}
          onReview={handleAdminTakedown}
          isSubmitting={modalSubmitting}
          error={modalError}
        />

        <ConfirmModal
          isOpen={isCloseModalOpen}
          title="Close internship"
          message="Close this internship? Closed postings cannot be reopened."
          confirmLabel="Close internship"
          confirmVariant="danger"
          onClose={() => setIsCloseModalOpen(false)}
          onConfirm={async () => {
            await handleClose();
            setIsCloseModalOpen(false);
          }}
        />
      </div>
    </AppShell>
  );
};
