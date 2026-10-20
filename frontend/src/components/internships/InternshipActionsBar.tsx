import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui';
import { InternshipStatusBadge } from './InternshipStatusBadge';
import { Internship } from '../../types/internship';

interface InternshipActionsBarProps {
  internship: Internship;
  isOwner: boolean;
  onSubmitForReview: () => void;
  onWithdrawToDraft: () => void;
  onClose: () => void;
}

export const InternshipActionsBar: React.FC<InternshipActionsBarProps> = ({
  internship,
  isOwner,
  onSubmitForReview,
  onWithdrawToDraft,
  onClose,
}) => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <InternshipStatusBadge status={internship.status} />
      {isOwner && (internship.status === 'draft' || internship.status === 'rejected') && (
        <>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(`/internships/${internship.id}/edit`)}
          >
            Edit
          </Button>
          <Button type="button" variant="primary" onClick={onSubmitForReview}>
            Submit for review
          </Button>
        </>
      )}
      {isOwner && internship.status === 'pending_review' && (
        <Button type="button" variant="secondary" onClick={onWithdrawToDraft}>
          Withdraw to draft
        </Button>
      )}
      {isOwner && internship.status === 'open' && (
        <>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(`/internships/${internship.id}/edit`)}
          >
            Extend deadline
          </Button>
          <Button type="button" variant="danger" onClick={onClose}>
            Close
          </Button>
        </>
      )}
    </div>
  );
};
