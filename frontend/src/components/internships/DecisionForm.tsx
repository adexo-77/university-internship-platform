import React, { useState } from 'react';
import { ApplicationStatus } from '../../types/application';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Textarea } from '../ui/Textarea';

export interface DecisionFormProps {
  currentStatus: ApplicationStatus;
  onSubmit: (status: 'shortlisted' | 'accepted' | 'rejected', message?: string) => Promise<void>;
  isSubmitting?: boolean;
  error?: string | null;
}

export const DecisionForm: React.FC<DecisionFormProps> = ({
  currentStatus,
  onSubmit,
  isSubmitting = false,
  error = null,
}) => {
  const [decisionMessage, setDecisionMessage] = useState('');
  const [targetStatus, setTargetStatus] = useState<'shortlisted' | 'accepted' | 'rejected' | null>(
    null
  );

  const isFinal =
    currentStatus === 'accepted' || currentStatus === 'rejected' || currentStatus === 'withdrawn';
  if (isFinal) {
    return null;
  }

  const handleAction = async (status: 'shortlisted' | 'accepted' | 'rejected') => {
    setTargetStatus(status);
    await onSubmit(status, decisionMessage.trim() || undefined);
    setTargetStatus(null);
  };

  return (
    <div className="space-y-4 max-w-xl">
      {error && <ErrorMessage whatHappened="Could not submit decision." howToFix={error} />}

      <Textarea
        id="decision-message"
        label="Decision message (optional)"
        value={decisionMessage}
        onChange={(e) => setDecisionMessage(e.target.value)}
        rows={3}
        placeholder="Add constructive feedback or next steps for the applicant (max 1000 characters)..."
      />

      <div className="flex flex-wrap items-center gap-3">
        {currentStatus === 'submitted' && (
          <Button
            type="button"
            variant="secondary"
            disabled={isSubmitting}
            onClick={() => handleAction('shortlisted')}
          >
            {isSubmitting && targetStatus === 'shortlisted' ? 'Updating...' : 'Shortlist'}
          </Button>
        )}

        <Button
          type="button"
          variant="primary"
          disabled={isSubmitting}
          onClick={() => handleAction('accepted')}
        >
          {isSubmitting && targetStatus === 'accepted' ? 'Updating...' : 'Accept'}
        </Button>

        <Button
          type="button"
          variant="danger"
          disabled={isSubmitting}
          onClick={() => handleAction('rejected')}
        >
          {isSubmitting && targetStatus === 'rejected' ? 'Updating...' : 'Reject'}
        </Button>
      </div>
    </div>
  );
};
