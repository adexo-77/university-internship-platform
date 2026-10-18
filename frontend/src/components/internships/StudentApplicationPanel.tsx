import React from 'react';
import { Link } from 'react-router-dom';
import { Application } from '../../types/application';
import { Internship } from '../../types/internship';
import { Button } from '../ui/Button';
import { Notice } from '../ui/Notice';
import { ApplicationStatusBadge } from './ApplicationStatusBadge';
import { ApplyForm } from './ApplyForm';

export interface StudentApplicationPanelProps {
  internship: Internship;
  myApp: Application | null;
  isProfileComplete: boolean;
  submitting: boolean;
  error: string | null;
  onApply: (coverLetter: string) => Promise<void>;
  onWithdraw: () => Promise<void>;
}

export const StudentApplicationPanel: React.FC<StudentApplicationPanelProps> = ({
  internship,
  myApp,
  isProfileComplete,
  submitting,
  error,
  onApply,
  onWithdraw,
}) => {
  return (
    <div className="pt-6 border-t border-line space-y-4">
      <h2 className="text-lg font-semibold text-ink">Your application</h2>

      {myApp ? (
        <div className="p-4 bg-surface rounded-card border border-line space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-ink">Status:</span>
              <ApplicationStatusBadge status={myApp.status} />
            </div>
            {(myApp.status === 'submitted' || myApp.status === 'shortlisted') && (
              <Button type="button" variant="quiet" disabled={submitting} onClick={onWithdraw}>
                {submitting ? 'Withdrawing...' : 'Withdraw'}
              </Button>
            )}
          </div>
          {myApp.decision_message && (
            <div className="pt-2 text-sm text-pencil border-t border-line">
              <span className="font-medium text-ink block">Message from organization:</span>
              {myApp.decision_message}
            </div>
          )}
        </div>
      ) : !internship.applications_accepted ? (
        <Notice variant="info">Applications closed</Notice>
      ) : !isProfileComplete ? (
        <Notice variant="attention">
          Complete your profile before applying.{' '}
          <Link to="/profile" className="text-petrol underline font-medium">
            Go to Profile
          </Link>
        </Notice>
      ) : (
        <ApplyForm onSubmit={onApply} isSubmitting={submitting} error={error} />
      )}
    </div>
  );
};
