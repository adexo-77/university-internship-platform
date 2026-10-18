import {
  Activity,
  BookMarked,
  BookOpen,
  Contact,
  User as UserIcon,
  type LucideIcon,
} from 'lucide-react';
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
    path: '/courses',
    label: 'Courses',
    icon: BookOpen,
    roles: ['student', 'admin'],
  },
  {
    path: '/my-courses',
    label: 'My courses',
    icon: BookMarked,
    roles: ['student', 'instructor'],
  },
  {
    path: '/profile',
    label: 'Profile',
    icon: Contact,
    roles: ['student', 'organization'],
  },
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
 */
export function getHomePath(role: UserRole): string {
  if (role === 'student' || role === 'instructor') {
    return '/my-courses';
  }
  if (role === 'organization') {
    return '/profile';
  }
  if (role === 'admin') {
    return '/courses';
  }
  return '/account';
}
