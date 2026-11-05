import React, { useState } from 'react';
import { enrollInCourse, leaveCourse } from '../../api/course';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';

export interface EnrollButtonProps {
  courseId: number;
  enrolled: boolean;
  hasGradedWork?: boolean;
  onEnrollmentChange: (newEnrolled: boolean) => void;
  disabled?: boolean;
}

export const EnrollButton: React.FC<EnrollButtonProps> = ({
  courseId,
  enrolled,
  hasGradedWork = false,
  onEnrollmentChange,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async () => {
    setError(null);
    setLoading(true);
    try {
      if (enrolled) {
        await leaveCourse(courseId);
        onEnrollmentChange(false);
      } else {
        await enrollInCourse(courseId);
        onEnrollmentChange(true);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to update course enrollment.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (enrolled && hasGradedWork) {
    return (
      <div className="flex flex-col items-start gap-1">
        <Button
          type="button"
          variant="secondary"
          disabled
          title="Cannot leave course after coursework has been graded"
        >
          Leave course
        </Button>
        <span className="text-xs text-pencil">Coursework graded (enrollment locked)</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <Button
        type="button"
        variant={enrolled ? 'secondary' : 'primary'}
        onClick={handleToggle}
        disabled={disabled || loading}
      >
        {loading
          ? enrolled
            ? 'Leaving...'
            : 'Enrolling...'
          : enrolled
            ? 'Leave course'
            : 'Enroll in course'}
      </Button>
      {error && (
        <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
      )}
    </div>
  );
};
