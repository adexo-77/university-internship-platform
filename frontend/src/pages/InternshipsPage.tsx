import React, { useCallback, useEffect, useState } from 'react';
import { getInternships } from '../api/internship';
import { InternshipTable } from '../components/internships/InternshipTable';
import { SuggestedInternshipsSection } from '../components/internships/SuggestedInternshipsSection';
import { AppShell } from '../components/layout/AppShell';
import { Button, ErrorMessage, PageHeader, Select, TextField } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { Internship } from '../types/internship';

const PAGE_SIZE = 10;

export const InternshipsPage: React.FC = () => {
  usePageTitle('Internships');
  const { user } = useAuth();
  const [internships, setInternships] = useState<Internship[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [workMode, setWorkMode] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPostings = useCallback(async (q: string, mode: string, currentOffset: number) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await getInternships({
        q: q.trim() || undefined,
        work_mode: mode || undefined,
        limit: PAGE_SIZE,
        offset: currentOffset,
      });
      setInternships(resp.items);
      setTotal(resp.total);
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
    fetchPostings(submittedQuery, workMode, offset);
  }, [fetchPostings, submittedQuery, workMode, offset]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    setSubmittedQuery(searchQuery);
  };

  const handleClear = () => {
    setSearchQuery('');
    setSubmittedQuery('');
    setWorkMode('');
    setOffset(0);
  };

  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setWorkMode(e.target.value);
    setOffset(0);
  };

  const canGoPrevious = offset > 0;
  const canGoNext = offset + PAGE_SIZE < total;

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader title="Internships" description="Browse available internship opportunities." />

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
        )}

        {user?.role === 'student' && <SuggestedInternshipsSection limit={5} />}

        <div className="bg-surface rounded-card p-4 border border-line">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3 items-end">
            <div className="flex-1 w-full">
              <TextField
                id="internship-search"
                label="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title or organization..."
              />
            </div>
            <div className="w-full md:w-48">
              <Select
                id="work-mode-filter"
                label="Work mode"
                value={workMode}
                onChange={handleModeChange}
                options={[
                  { value: '', label: 'All work modes' },
                  { value: 'remote', label: 'Remote' },
                  { value: 'hybrid', label: 'Hybrid' },
                  { value: 'onsite', label: 'Onsite' },
                ]}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" variant="secondary" disabled={loading}>
                Search
              </Button>
              {(submittedQuery || workMode) && (
                <Button type="button" variant="quiet" onClick={handleClear} disabled={loading}>
                  Clear
                </Button>
              )}
            </div>
          </form>
        </div>

        {loading ? (
          <div className="p-8 text-center text-pencil">Loading internships...</div>
        ) : (
          <div className="space-y-4">
            <InternshipTable
              internships={internships}
              showStatus={user?.role === 'admin' || user?.role === 'coordinator'}
              showApplicantCount={user?.role === 'admin' || user?.role === 'coordinator'}
              showOrganization={true}
              showApplicationStatus={user?.role === 'student'}
              emptyMessage="No internships match your criteria."
            />

            {total > 0 && (
              <div className="flex items-center justify-between text-sm text-pencil pt-2">
                <span>
                  Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total} postings
                </span>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="quiet"
                    disabled={!canGoPrevious || loading}
                    onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
                  >
                    Previous
                  </Button>
                  <Button
                    type="button"
                    variant="quiet"
                    disabled={!canGoNext || loading}
                    onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
};
