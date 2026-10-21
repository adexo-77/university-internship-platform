import React from 'react';
import { Link } from 'react-router-dom';
import { Notice } from '../ui/Notice';

export interface InternshipReviewNoticeProps {
  status: string;
  reviewNote?: string | null;
  isOwner: boolean;
  internshipId: number;
}

export const InternshipReviewNotice: React.FC<InternshipReviewNoticeProps> = ({
  status,
  reviewNote,
  isOwner,
  internshipId,
}) => {
  if (status !== 'rejected' || !reviewNote) return null;

  return (
    <Notice variant="error" title="Review note">
      <p className="whitespace-pre-line">{reviewNote}</p>
      {isOwner && (
        <p className="mt-2 text-sm">
          <span>You can edit this posting to address feedback and resubmit it for review. </span>
          <Link
            to={`/internships/${internshipId}/edit`}
            className="font-semibold text-petrol underline"
          >
            Edit posting
          </Link>
        </p>
      )}
    </Notice>
  );
};
