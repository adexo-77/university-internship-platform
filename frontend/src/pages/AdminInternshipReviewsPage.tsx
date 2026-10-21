import React, { useCallback, useEffect, useState } from 'react';
import { listAdminInternships, reviewInternship } from '../api/admin_internship';
import { AdminInternshipReviewModal } from '../components/admin/AdminInternshipReviewModal';
import { AdminInternshipReviewsTable } from '../components/admin/AdminInternshipReviewsTable';
import { AppShell } from '../components/layout/AppShell';
import { ErrorMessage, PageHeader, Select } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { Internship } from '../types/internship';

const STATUS_OPTIONS = [
  { value: 'pending_review', label: 'Pending review' },
  { value: 'open', label: 'Open' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'closed', label: 'Closed' },
  { value: 'all', label: 'All' },
];

export const AdminInternshipReviewsPage: React.FC = () => {
  usePageTitle('Internship reviews');

  const [internships, setInternships] = useState<Internship[]>([]);
  const [statusFilter, setStatusFilter] = useState('pending_review');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedPosting, setSelectedPosting] = useState<Internship | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAdminInternships({ status: statusFilter });
      setInternships(data.items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load internship reviews.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleReview = async (decision: 'approved' | 'rejected', reviewNote?: string) => {
    if (!selectedPosting) return;
    setSubmitting(true);
    setModalError(null);
    try {
      const updated = await reviewInternship(selectedPosting.id, {
        decision,
        review_note: reviewNote,
      });
      setSelectedPosting(null);
      setInternships((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err: unknown) {
      setModalError(err instanceof Error ? err.message : 'Failed to submit review decision.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Internship reviews"
          description="Review submitted internship postings and manage active listings."
        />

        <div className="flex items-center gap-4">
          <div className="w-56">
            <Select
              id="admin-status-filter"
              label="Status filter"
              value={statusFilter}
              options={STATUS_OPTIONS}
              onChange={(e) => setStatusFilter(e.target.value)}
            />
          </div>
        </div>

        {error && <ErrorMessage whatHappened={error} howToFix="Please try refreshing the page." />}

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading internship reviews...</div>
        ) : (
          <AdminInternshipReviewsTable
            internships={internships}
            onSelect={(item) => {
              setModalError(null);
              setSelectedPosting(item);
            }}
          />
        )}

        <AdminInternshipReviewModal
          internship={selectedPosting}
          isOpen={selectedPosting !== null}
          onClose={() => {
            setSelectedPosting(null);
            setModalError(null);
          }}
          onReview={handleReview}
          isSubmitting={submitting}
          error={modalError}
        />
      </div>
    </AppShell>
  );
};
