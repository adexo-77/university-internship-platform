import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getInternshipById, updateInternship } from '../api/internship';
import { getOrganizationProfile } from '../api/profile';
import { InternshipForm, InternshipFormData } from '../components/internships/InternshipForm';
import { OrganizationApprovalNotice } from '../components/internships/OrganizationApprovalNotice';
import { AppShell } from '../components/layout/AppShell';
import { ErrorMessage, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { Internship } from '../types/internship';
import { OrganizationProfile } from '../types/profile';

export const InternshipEditPage: React.FC = () => {
  usePageTitle('Edit internship');
  const { id } = useParams<{ id: string }>();
  const postingId = Number(id);
  const navigate = useNavigate();

  const [internship, setInternship] = useState<Internship | null>(null);
  const [profile, setProfile] = useState<OrganizationProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!postingId) return;
    setLoading(true);
    Promise.all([getInternshipById(postingId), getOrganizationProfile().catch(() => null)])
      .then(([data, prof]) => {
        setProfile(prof);
        if (data.status === 'closed') {
          setError('A closed internship posting cannot be edited.');
        } else {
          setInternship(data);
        }
      })
      .catch((err: unknown) => {
        if (err instanceof Error) setError(err.message);
        else setError('Failed to load internship.');
      })
      .finally(() => setLoading(false));
  }, [postingId]);

  const handleSubmit = async (data: InternshipFormData) => {
    if (!postingId) return;
    setSubmitting(true);
    setError(null);
    try {
      await updateInternship(postingId, data);
      navigate(`/internships/${postingId}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to update internship.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="p-8 text-center text-pencil">Loading details...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <div>
          <Link
            to={`/internships/${postingId}`}
            className="text-sm text-petrol hover:underline font-medium mb-2 inline-block"
          >
            &larr; Back to internship
          </Link>
          <PageHeader
            title="Edit internship"
            description="Update the details of your internship posting."
          />
        </div>

        <OrganizationApprovalNotice profile={profile} />

        {error && !internship ? (
          <ErrorMessage
            whatHappened={error}
            howToFix="Please try again or return to the posting."
          />
        ) : (
          internship && (
            <InternshipForm
              initialData={internship}
              onSubmit={handleSubmit}
              isSubmitting={submitting}
              isEdit={true}
              error={error}
              onCancel={() => navigate(`/internships/${postingId}`)}
            />
          )
        )}
      </div>
    </AppShell>
  );
};
