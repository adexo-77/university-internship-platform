import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { getAssignment, gradeSubmission, listAssignmentSubmissions } from '../api/assignment';
import { GradeForm } from '../components/assignments/GradeForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui/PageHeader';
import {
  Assignment,
  StudentSubmissionRosterItem,
  SubmissionGradePayload,
} from '../types/assignment';

export const SubmissionGradePage: React.FC = () => {
  const { assignmentId, submissionId } = useParams<{
    assignmentId: string;
    submissionId: string;
  }>();
  const navigate = useNavigate();

  const numAssignmentId = Number(assignmentId);
  const numSubmissionId = Number(submissionId);

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [rosterItem, setRosterItem] = useState<StudentSubmissionRosterItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [assignData, rosterData] = await Promise.all([
          getAssignment(numAssignmentId),
          listAssignmentSubmissions(numAssignmentId),
        ]);
        if (!mounted) return;
        setAssignment(assignData);

        const found = rosterData.find((item) => item.submission?.id === numSubmissionId);
        if (!found || !found.submission) {
          setError('Submission not found.');
        } else {
          setRosterItem(found);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load grading details.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    if (!isNaN(numAssignmentId) && !isNaN(numSubmissionId)) {
      load();
    }

    return () => {
      mounted = false;
    };
  }, [numAssignmentId, numSubmissionId]);

  const handleGradeSubmit = async (data: SubmissionGradePayload) => {
    await gradeSubmission(numSubmissionId, data);
    navigate(`/assignments/${numAssignmentId}`);
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <PageHeader
          title={rosterItem ? `Grade submission: ${rosterItem.student_name}` : 'Grade submission'}
          description={assignment ? `Assignment: ${assignment.title}` : 'Score student coursework.'}
          actions={
            <Link
              to={`/assignments/${numAssignmentId}`}
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
            >
              Back to assignment
            </Link>
          }
        />

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading student submission...</div>
        ) : error || !assignment || !rosterItem || !rosterItem.submission ? (
          <div className="rounded-control border border-brick bg-brick-tint/20 p-6 text-center text-brick">
            {error || 'Unable to load submission.'}
          </div>
        ) : (
          <div className="rounded-control border border-line bg-surface p-6 shadow-subtle">
            <GradeForm
              submission={rosterItem.submission}
              maxPoints={assignment.max_points}
              onSubmit={handleGradeSubmit}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
};
