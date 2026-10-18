import React, { useState } from 'react';
import { enrollInCourse, leaveCourse } from '../../api/course';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';

export interface EnrollButtonProps {
  courseId: number;
  enrolled: boolean;
  onEnrollmentChange: (newEnrolled: boolean) => void;
  disabled?: boolean;
}

export const EnrollButton: React.FC<EnrollButtonProps> = ({
  courseId,
  enrolled,
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

  return (
    <div className="flex flex-col items-start gap-2">
      <Button
        type="button"
        variant={enrolled ? 'outline' : 'primary'}
        onClick={handleToggle}
        loading={loading}
        disabled={disabled || loading}
      >
        {enrolled ? 'Leave course' : 'Enroll in course'}
      </Button>
      {error && <ErrorMessage message={error} />}
    </div>
  );
};
