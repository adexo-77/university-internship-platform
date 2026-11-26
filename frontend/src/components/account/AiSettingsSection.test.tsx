import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAiStatus } from '../../hooks/useAiStatus';
import { AiSettingsSection } from './AiSettingsSection';

vi.mock('../../hooks/useAiStatus', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../hooks/useAiStatus')>();
  return {
    ...actual,
    useAiStatus: vi.fn(),
  };
});

const baseStatus = {
  enabled: true,
  consented: false,
  consent_at: null,
  remaining_quota: 10,
  daily_limit: 10,
};

function mockHook(overrides: Partial<ReturnType<typeof useAiStatus>>) {
  vi.mocked(useAiStatus).mockReturnValue({
    status: baseStatus,
    isLoading: false,
    isSaving: false,
    error: null,
    refetch: vi.fn(),
    setConsent: vi.fn(),
    ...overrides,
  });
}

describe('AiSettingsSection Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state', () => {
    mockHook({ isLoading: true, status: null });
    render(<AiSettingsSection />);
    expect(screen.getByText(/loading your ai assistance settings/i)).toBeInTheDocument();
  });

  it('shows error notice when status fails to load', () => {
    mockHook({ status: null, error: 'network down' });
    render(<AiSettingsSection />);
    expect(screen.getByText(/unable to load ai settings/i)).toBeInTheDocument();
    expect(screen.getByText(/network down/i)).toBeInTheDocument();
  });

  it('explains privacy and shows disabled notice when globally off', () => {
    mockHook({ status: { ...baseStatus, enabled: false } });
    render(<AiSettingsSection />);
    expect(
      screen.getByText(/disabled globally by the platform administrator/i)
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /enable ai assistance/i })).not.toBeInTheDocument();
  });

  it('toggles consent when enabled', async () => {
    const setConsent = vi.fn();
    mockHook({ setConsent });
    render(<AiSettingsSection />);

    fireEvent.click(screen.getByRole('button', { name: /enable ai assistance/i }));
    expect(setConsent).toHaveBeenCalledWith(true);
  });

  it('shows remaining quota when consented', () => {
    mockHook({ status: { ...baseStatus, consented: true, remaining_quota: 4 } });
    render(<AiSettingsSection />);
    expect(screen.getByText(/4 of 10 daily requests remaining/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /withdraw consent/i })).toBeInTheDocument();
  });

  it('surfaces update errors', () => {
    mockHook({ error: 'update failed' });
    render(<AiSettingsSection />);
    expect(screen.getByText(/could not update consent/i)).toBeInTheDocument();
  });
});
