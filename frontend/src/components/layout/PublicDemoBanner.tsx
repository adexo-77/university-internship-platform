import React from 'react';
import { useHealth } from '../../hooks/useHealth';

export interface PublicDemoBannerProps {
  enabled?: boolean;
}

const BannerMessage: React.FC = () => (
  <div
    role="status"
    data-testid="public-demo-banner"
    className="w-full bg-petrol-tint text-ink border-b border-line px-4 py-1.5 text-center text-xs font-medium"
  >
    Public demo: fictional data that may be reset at any time
  </div>
);

const PublicDemoBannerFromHealth: React.FC = () => {
  const { publicDemo } = useHealth();
  if (!publicDemo) {
    return null;
  }
  return <BannerMessage />;
};

export const PublicDemoBanner: React.FC<PublicDemoBannerProps> = ({ enabled }) => {
  if (enabled !== undefined) {
    return enabled ? <BannerMessage /> : null;
  }
  return <PublicDemoBannerFromHealth />;
};
