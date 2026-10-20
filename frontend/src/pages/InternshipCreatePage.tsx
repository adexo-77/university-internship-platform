import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createInternship } from '../api/internship';
import { getOrganizationProfile } from '../api/profile';
import { InternshipForm, InternshipFormData } from '../components/internships/InternshipForm';
import { OrganizationApprovalNotice } from '../components/internships/OrganizationApprovalNotice';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { OrganizationProfile } from '../types/profile';

export const InternshipCreatePage: React.FC = () => {
  usePageTitle('New internship');
  const navigate = useNavigate();
  const [profile, setProfile] = useState<OrganizationProfile | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOrganizationProfile()
      .then((data) => setProfile(data))
      .catch(() => null);
  }, []);

  const handleSubmit = async (data: InternshipFormData) => {
    setSubmitting(true);
    setError(null);
    try {
      const created = await createInternship(data);
      navigate(`/internships/${created.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create internship.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <div>
          <Link
            to="/my-internships"
            className="text-sm text-petrol hover:underline font-medium mb-2 inline-block"
          >
            &larr; Back to my internships
          </Link>
          <PageHeader
            title="New internship"
            description="Create an internship posting in draft status."
          />
        </div>

        <OrganizationApprovalNotice profile={profile} />

        <InternshipForm
          onSubmit={handleSubmit}
          isSubmitting={submitting}
          error={error}
          onCancel={() => navigate('/my-internships')}
        />
      </div>
    </AppShell>
  );
};
