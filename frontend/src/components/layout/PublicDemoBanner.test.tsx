import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as healthApi from '../../api/health';
import { PublicDemoBanner } from './PublicDemoBanner';

describe('PublicDemoBanner Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders nothing when public demo mode is disabled', () => {
    const { container } = render(<PublicDemoBanner enabled={false} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders the slim banner when public demo mode is enabled', () => {
    render(<PublicDemoBanner enabled={true} />);

    const banner = screen.getByRole('status');
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent('Public demo: fictional data that may be reset at any time');
    expect(banner).toHaveClass('bg-petrol-tint', 'text-ink', 'border-b', 'border-line');
  });

  it('renders banner automatically when hook reports public demo mode', async () => {
    vi.spyOn(healthApi, 'fetchHealth').mockResolvedValueOnce({
      status: 'ok',
      public_demo: true,
    });
    vi.spyOn(healthApi, 'fetchDatabaseHealth').mockResolvedValueOnce({
      database: 'ok',
    });

    render(<PublicDemoBanner />);

    const banner = await screen.findByRole('status');
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent('Public demo: fictional data that may be reset at any time');
  });
});
