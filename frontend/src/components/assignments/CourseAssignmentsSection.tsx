import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCourseAssignments } from '../../api/assignment';
import { Assignment } from '../../types/assignment';
import { Button } from '../ui/Button';
import { AssignmentTable } from './AssignmentTable';

export interface CourseAssignmentsSectionProps {
  courseId: number;
  isOwner?: boolean;
  isAdmin?: boolean;
  isStudent?: boolean;
}

export const CourseAssignmentsSection: React.FC<CourseAssignmentsSectionProps> = ({
  courseId,
  isOwner = false,
  isAdmin = false,
  isStudent = false,
}) => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await listCourseAssignments(courseId);
        if (mounted) setAssignments(data);
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load course assignments.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [courseId]);

  return (
    <section className="space-y-4 pt-4 border-t border-line">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-ink">Assignments ({assignments.length})</h2>
          <p className="text-sm text-pencil">
            Course coursework, problem sets, and practical assignments.
          </p>
        </div>
        {isOwner && (
          <Link to={`/courses/${courseId}/assignments/new`}>
            <Button size="sm">New assignment</Button>
          </Link>
        )}
      </div>

      {loading ? (
        <div className="py-8 text-center text-sm text-pencil">Loading assignments...</div>
      ) : error ? (
        <div className="rounded-control border border-brick bg-surface p-4 text-sm text-brick">
          {error}
        </div>
      ) : (
        <AssignmentTable
          assignments={assignments}
          courseId={courseId}
          isOwner={isOwner}
          isAdmin={isAdmin}
          isStudent={isStudent}
        />
      )}
    </section>
  );
};
