import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createInternship } from '../api/internship';
import { InternshipForm, InternshipFormData } from '../components/internships/InternshipForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';

export const InternshipCreatePage: React.FC = () => {
  usePageTitle('New internship');
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
