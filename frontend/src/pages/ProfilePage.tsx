import React from 'react';
import { StudentBadgesSection } from '../components/badges/StudentBadgesSection';
import { AppShell } from '../components/layout/AppShell';
import { OrganizationProfileForm } from '../components/profile/OrganizationProfileForm';
import { StudentProfileForm } from '../components/profile/StudentProfileForm';
import { PageHeader } from '../components/ui';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';

export const ProfilePage: React.FC = () => {
  usePageTitle('Profile');
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <PageHeader
          title="Profile"
          description={
            user.role === 'student'
              ? 'Manage your academic details, skills, and background for internship applications.'
              : 'Manage your organization profile, sector, and company description.'
          }
        />

        {user.role === 'student' && (
          <div className="space-y-8">
            <StudentProfileForm />
            <div className="pt-6 border-t border-line">
              <StudentBadgesSection />
            </div>
          </div>
        )}
        {user.role === 'organization' && <OrganizationProfileForm />}
      </div>
    </AppShell>
  );
};
