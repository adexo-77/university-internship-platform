import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getAssignment,
  getStudentSubmission,
  listAssignmentSubmissions,
  submitAssignment,
} from '../api/assignment';
import { DueBadge } from '../components/assignments/DueBadge';
import { SubmissionForm } from '../components/assignments/SubmissionForm';
import { SubmissionsTable } from '../components/assignments/SubmissionsTable';
import { AppShell } from '../components/layout/AppShell';
import { Badge } from '../components/ui/Badge';
import { Notice } from '../components/ui/Notice';
import { PageHeader } from '../components/ui/PageHeader';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import {
  Assignment,
  StudentSubmissionRosterItem,
  Submission,
  SubmissionSubmitPayload,
} from '../types/assignment';

export const AssignmentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const numericId = Number(id);
  const { user } = useAuth();

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  usePageTitle(assignment ? assignment.title : 'Assignment details');
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [roster, setRoster] = useState<StudentSubmissionRosterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const isStudent = user?.role === 'student';
  const isInstructor = user?.role === 'instructor';
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const assignData = await getAssignment(numericId);
        if (!mounted) return;
        setAssignment(assignData);

        if (isStudent) {
          try {
            const subData = await getStudentSubmission(numericId);
            if (mounted) setSubmission(subData);
          } catch {
            // No submission yet, which is expected
          }
        } else if (isInstructor || isAdmin) {
          try {
            const rosterData = await listAssignmentSubmissions(numericId);
            if (mounted) setRoster(rosterData);
          } catch {
            // Handled if non-owner
          }
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load assignment details.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    if (!isNaN(numericId)) {
      loadData();
    }

    return () => {
      mounted = false;
    };
  }, [numericId, isStudent, isInstructor, isAdmin]);

  const handleStudentSubmit = async (data: SubmissionSubmitPayload) => {
    const updated = await submitAssignment(numericId, data);
    setSubmission(updated);
    setNotice('Your work has been submitted successfully.');
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        {notice && <Notice variant="info">{notice}</Notice>}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading assignment details...</div>
        ) : error || !assignment ? (
          <div className="rounded-control border border-brick bg-brick-tint/20 p-6 text-center text-brick">
            {error || 'Assignment not found.'}
          </div>
        ) : (
          <>
            <PageHeader
              title={assignment.title}
              description={`Course #${assignment.course_id}`}
              actions={
                <div className="flex items-center gap-3">
                  <Link
                    to={`/courses/${assignment.course_id}`}
                    className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
                  >
                    Back to course
                  </Link>
                  {(isInstructor || isAdmin) && (
                    <Link
                      to={`/assignments/${assignment.id}/edit`}
                      className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
                    >
                      Edit assignment
                    </Link>
                  )}
                </div>
              }
            />

            <div className="flex items-center gap-4 flex-wrap pb-2 border-b border-line">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-pencil uppercase tracking-wider">
                  Due:
                </span>
                <DueBadge dueAt={assignment.due_at} />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-pencil uppercase tracking-wider">
                  Points:
                </span>
                <Badge variant="neutral">{assignment.max_points} max points</Badge>
              </div>
            </div>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold text-ink">Instructions</h2>
              <div className="rounded-control border border-line bg-surface p-6 text-ink whitespace-pre-wrap leading-relaxed">
                {assignment.description || 'No instructions provided for this assignment.'}
              </div>
            </section>

            {isStudent && (
              <section className="space-y-4 pt-4 border-t border-line">
                <h2 className="text-lg font-semibold text-ink">Your submission</h2>
                <SubmissionForm
                  submission={submission}
                  maxPoints={assignment.max_points}
                  onSubmit={handleStudentSubmit}
                />
              </section>
            )}

            {(isInstructor || isAdmin) && (
              <section className="space-y-4 pt-4 border-t border-line">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-ink">Student submissions</h2>
                    <p className="text-sm text-pencil">
                      Track student progress, check submission times, and assign grades.
                    </p>
                  </div>
                </div>

                <SubmissionsTable
                  roster={roster}
                  assignmentId={assignment.id}
                  maxPoints={assignment.max_points}
                  isOwner={isInstructor}
                />
              </section>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
};
