import React from 'react';
import { OrganizationProfile } from '../../types/profile';
import { Notice } from '../ui';

export interface OrganizationApprovalNoticeProps {
  profile: OrganizationProfile | null;
}

export const OrganizationApprovalNotice: React.FC<OrganizationApprovalNoticeProps> = ({
  profile,
}) => {
  if (!profile || profile.approval_status === 'approved') {
    return null;
  }

  if (profile.approval_status === 'rejected') {
    return (
      <Notice variant="error" title="Application rejected">
        {profile.approval_note
          ? profile.approval_note
          : 'Your organization application was rejected. Please contact an administrator.'}
      </Notice>
    );
  }

  return (
    <Notice variant="attention" title="Approval pending">
      Your organization is awaiting approval. You can prepare drafts, but you cannot publish until
      an admin approves you.
    </Notice>
  );
};
