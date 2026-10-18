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
 */
export const navigationItems: NavItem[] = [
  {
    path: '/account',
    label: 'Account',
    icon: UserIcon,
  },
  {
    path: '/',
    label: 'System status',
    icon: Activity,
    roles: ['admin'],
  },
];
