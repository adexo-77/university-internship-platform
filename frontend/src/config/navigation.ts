import { Activity, User as UserIcon, type LucideIcon } from 'lucide-react';
import { UserRole } from '../types/auth';

export interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
}

/**
 * Platform navigation items.
 * Only pages that exist are listed; roles restrict visibility per user role.
 * Each phase adds items here — no hard-coded items elsewhere.
 */
export const navigationItems: NavItem[] = [
  {
    path: '/account',
    label: 'Account',
    icon: UserIcon,
  },
  {
    path: '/status',
    label: 'System status',
    icon: Activity,
    roles: ['admin'],
  },
];

/**
 * Returns the default home path for a given user role.
 * Later phases update this function to route each role to its own landing page.
 */
export function getHomePath(role: UserRole): string {
  // All roles currently land on /account. Future phases will branch on `role`.
  void role;
  return '/account';
}
