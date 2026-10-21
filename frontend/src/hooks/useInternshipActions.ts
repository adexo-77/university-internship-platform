import { useState } from 'react';
import { closeInternship, submitInternship, withdrawInternship } from '../api/internship';
import { applyToInternship, withdrawApplication } from '../api/application';
import { Internship } from '../types/internship';

export function useInternshipActions(
  internship: Internship | null,
  postingId: number,
  onSuccess: () => Promise<void>
) {
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const handleApply = async (coverLetter: string) => {
    setSubmitting(true);
    setActionError(null);
    try {
      await applyToInternship(postingId, { cover_letter: coverLetter });
      await onSuccess();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to submit application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWithdraw = async (myAppId?: number) => {
    if (!myAppId) return;
    setSubmitting(true);
    setActionError(null);
    try {
      await withdrawApplication(myAppId);
      await onSuccess();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to withdraw application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!internship) return;
    setActionError(null);
    try {
      await submitInternship(internship.id);
      await onSuccess();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to submit for review.');
    }
  };

  const handleWithdrawToDraft = async () => {
    if (!internship) return;
    setActionError(null);
    try {
      await withdrawInternship(internship.id);
      await onSuccess();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to withdraw to draft.');
    }
  };

  const handleClose = async () => {
    if (!internship) return;
    setActionError(null);
    try {
      await closeInternship(internship.id);
      await onSuccess();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to close internship.');
    }
  };

  return {
    submitting,
    actionError,
    setActionError,
    handleApply,
    handleWithdraw,
    handleSubmitForReview,
    handleWithdrawToDraft,
    handleClose,
  };
}
