import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  closeInternship,
  getOrganizationInternships,
  submitInternship,
  withdrawInternship,
} from '../api/internship';
import { getOrganizationProfile } from '../api/profile';
import { InternshipTable } from '../components/internships/InternshipTable';
import { OrganizationApprovalNotice } from '../components/internships/OrganizationApprovalNotice';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, Notice, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { Internship } from '../types/internship';
import { OrganizationProfile } from '../types/profile';

export const MyInternshipsPage: React.FC = () => {
  usePageTitle('My internships');
  const navigate = useNavigate();
  const [internships, setInternships] = useState<Internship[]>([]);
  const [profile, setProfile] = useState<OrganizationProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPostings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [data, prof] = await Promise.all([
        getOrganizationInternships(),
        getOrganizationProfile().catch(() => null),
      ]);
      setInternships(data);
      setProfile(prof);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load internships.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPostings();
  }, [fetchPostings]);

  const handleSubmitForReview = async (id: number) => {
    try {
      await submitInternship(id);
      await fetchPostings();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

  const handleWithdraw = async (id: number) => {
    try {
      await withdrawInternship(id);
      await fetchPostings();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

  const handleClose = async (id: number) => {
    if (!window.confirm('Close this internship? Closed postings cannot be reopened.')) return;
    try {
      await closeInternship(id);
      await fetchPostings();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

  const isApproved = profile?.approval_status === 'approved';

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <PageHeader
            title="My internships"
            description="Manage your organization's internship postings and review applicants."
          />
          <Button type="button" variant="primary" onClick={() => navigate('/internships/new')}>
            New internship
          </Button>
        </div>

        <OrganizationApprovalNotice profile={profile} />

        {internships.some((i) => i.status === 'rejected' && i.review_note) && (
          <div className="space-y-3">
            {internships
              .filter((i) => i.status === 'rejected' && i.review_note)
              .map((i) => (
                <Notice key={i.id} variant="attention">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <span>
                      <strong>{i.title}</strong> was rejected by an admin: &ldquo;{i.review_note}
                      &rdquo;
                    </span>
                    <Link
                      to={`/internships/${i.id}/edit`}
                      className="font-medium text-petrol underline whitespace-nowrap"
                    >
                      Edit posting
                    </Link>
                  </div>
                </Notice>
              ))}
          </div>
        )}

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading your internships...</div>
        ) : (
          <InternshipTable
            internships={internships}
            showStatus={true}
            showOrganization={false}
            showApplicantCount={true}
            emptyMessage="You have not created any internship postings yet."
            actionRenderer={(item) => (
              <div className="flex items-center gap-2">
                {(item.status === 'draft' || item.status === 'rejected') && (
                  <>
                    <Button
                      type="button"
                      variant="quiet"
                      disabled={!isApproved}
                      title={
                        !isApproved
                          ? 'Your organization must be approved before you can submit internships for review.'
                          : undefined
                      }
                      onClick={() => handleSubmitForReview(item.id)}
                    >
                      Submit for review
                    </Button>
                    <Button
                      type="button"
                      variant="quiet"
                      onClick={() => navigate(`/internships/${item.id}/edit`)}
                    >
                      Edit
                    </Button>
                  </>
                )}
                {item.status === 'pending_review' && (
                  <Button type="button" variant="quiet" onClick={() => handleWithdraw(item.id)}>
                    Withdraw to draft
                  </Button>
                )}
                {item.status === 'open' && (
                  <>
                    <Button
                      type="button"
                      variant="quiet"
                      onClick={() => navigate(`/internships/${item.id}/edit`)}
                    >
                      Edit
                    </Button>
                    <Button type="button" variant="quiet" onClick={() => handleClose(item.id)}>
                      Close
                    </Button>
                  </>
                )}
              </div>
            )}
          />
        )}
      </div>
    </AppShell>
  );
};
