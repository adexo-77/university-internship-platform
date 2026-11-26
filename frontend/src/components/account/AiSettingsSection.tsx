import React from 'react';
import { useAiStatus } from '../../hooks/useAiStatus';
import { Button, Notice } from '../ui';

export const AiSettingsSection: React.FC = () => {
  const { status, isLoading, isSaving, error, setConsent } = useAiStatus();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-ink">AI assistance</h2>
        <p className="text-sm text-pencil">Loading your AI assistance settings...</p>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-ink">AI assistance</h2>
        <Notice variant="error" title="Unable to load AI settings">
          {error}
        </Notice>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-ink">AI assistance</h2>
        <Notice variant="error" title="Unable to load AI settings">
          Please try again later.
        </Notice>
      </div>
    );
  }

  const { enabled, consented, remaining_quota, daily_limit } = status;
  const isEnabled = enabled;
  const toggleLabel = consented ? 'Withdraw consent' : 'Enable AI assistance';

  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold text-ink">AI assistance</h2>

      <p className="text-sm text-pencil">
        AI assistance is an optional, opt-in feature. When enabled, it can generate draft
        suggestions to support your work. You stay in control and should always review any output
        before using it.
      </p>

      <Notice variant="info" title="What data is used">
        Only the feature name and a hashed token count are sent to the AI provider. Your name,
        email, and any submission text never leave the platform.
      </Notice>

      {!isEnabled && (
        <Notice variant="attention" title="AI assistance is disabled">
          AI assistance is disabled globally by the platform administrator.
        </Notice>
      )}

      {isEnabled && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-control border border-line bg-surface p-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-ink">
                {consented ? 'AI assistance is on' : 'AI assistance is off'}
              </p>
              <p className="text-xs text-pencil">
                {consented
                  ? `${remaining_quota} of ${daily_limit} daily requests remaining.`
                  : 'Enable to allow AI-generated draft suggestions.'}
              </p>
            </div>
            <Button
              variant={consented ? 'secondary' : 'primary'}
              onClick={() => void setConsent(!consented)}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : toggleLabel}
            </Button>
          </div>

          {error && (
            <Notice variant="error" title="Could not update consent">
              {error}
            </Notice>
          )}
        </>
      )}
    </div>
  );
};
