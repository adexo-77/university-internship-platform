import React, { useCallback, useEffect, useState } from 'react';
import { getCourses } from '../api/course';
import { CourseTable } from '../components/courses/CourseTable';
import { AppShell } from '../components/layout/AppShell';
import { Button, EmptyState, ErrorMessage, PageHeader, TextField } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { Course } from '../types/course';

const PAGE_SIZE = 10;

export const CoursesPage: React.FC = () => {
  usePageTitle('Courses');
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCourses = useCallback(async (q: string, currentOffset: number) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await getCourses({
        q: q.trim() || undefined,
        limit: PAGE_SIZE,
        offset: currentOffset,
      });
      setCourses(resp.items);
      setTotal(resp.total);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load courses.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCourses(submittedQuery, offset);
  }, [fetchCourses, submittedQuery, offset]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    setSubmittedQuery(searchQuery);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSubmittedQuery('');
    setOffset(0);
  };

  const hasNextPage = offset + PAGE_SIZE < total;
  const hasPrevPage = offset > 0;

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Courses"
          description="Explore available courses and enroll in your topics of study."
        />

        <form onSubmit={handleSearchSubmit} className="flex items-center gap-3 max-w-md">
          <div className="flex-1">
            <TextField
              id="course-search"
              label="Search courses"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by course title..."
            />
          </div>
          <div className="pt-6 flex gap-2">
            <Button type="submit" variant="secondary">
              Search
            </Button>
            {submittedQuery && (
              <Button type="button" variant="quiet" onClick={handleClearSearch}>
                Clear
              </Button>
            )}
          </div>
        </form>

        {error && (
          <ErrorMessage
            whatHappened={error}
            howToFix="Please try reloading the course list or refine your search."
          />
        )}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading courses...</div>
        ) : courses.length === 0 ? (
          <EmptyState
            title="No courses found"
            description={
              submittedQuery
                ? `No courses matched "${submittedQuery}". Try adjusting your search query.`
                : 'There are no published courses available at this time.'
            }
          />
        ) : (
          <div className="space-y-4">
            <CourseTable
              courses={courses}
              showStatus={user?.role === 'admin'}
              showEnrolledBadge={user?.role === 'student'}
            />

            <div className="flex items-center justify-between text-sm text-pencil pt-2">
              <div>
                Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total} courses
              </div>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  disabled={!hasPrevPage}
                  onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
                >
                  Previous
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  disabled={!hasNextPage}
                  onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};
