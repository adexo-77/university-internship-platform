import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOrganizationInternships, updateInternship } from '../api/internship';
import { getOrganizationProfile } from '../api/profile';
import { InternshipTable } from '../components/internships/InternshipTable';
import { OrganizationApprovalNotice } from '../components/internships/OrganizationApprovalNotice';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader } from '../components/ui';
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

  const handlePublish = async (id: number) => {
    if (!window.confirm('Publish this internship to make it open for applications?')) return;
    try {
      await updateInternship(id, { status: 'open' });
      await fetchPostings();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

  const handleClose = async (id: number) => {
    if (!window.confirm('Close this internship? Closed postings cannot be reopened.')) return;
    try {
      await updateInternship(id, { status: 'closed' });
      await fetchPostings();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    }
  };

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
                {item.status === 'draft' && (
                  <Button
                    type="button"
                    variant="quiet"
                    disabled={profile?.approval_status !== 'approved'}
                    title={
                      profile?.approval_status !== 'approved'
                        ? profile?.approval_status === 'rejected'
                          ? (profile.approval_note ?? 'Your organization application was rejected.')
                          : 'Your organization is awaiting approval. You can prepare drafts, but you cannot publish until an admin approves you.'
                        : undefined
                    }
                    onClick={() => handlePublish(item.id)}
                  >
                    Publish
                  </Button>
                )}
                {item.status === 'open' && (
                  <Button type="button" variant="quiet" onClick={() => handleClose(item.id)}>
                    Close
                  </Button>
                )}
                {item.status !== 'closed' && (
                  <Button
                    type="button"
                    variant="quiet"
                    onClick={() => navigate(`/internships/${item.id}/edit`)}
                  >
                    Edit
                  </Button>
                )}
              </div>
            )}
          />
        )}
      </div>
    </AppShell>
  );
};
