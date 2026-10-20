import {
  Activity,
  BookMarked,
  BookOpen,
  Briefcase,
  Building2,
  Contact,
  FileText,
  User as UserIcon,
  Users,
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
    path: '/admin/users',
    label: 'Users',
    icon: Users,
    roles: ['admin'],
  },
  {
    path: '/admin/organizations',
    label: 'Organizations',
    icon: Building2,
    roles: ['admin'],
  },
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
    path: '/internships',
    label: 'Internships',
    icon: Briefcase,
    roles: ['student', 'admin'],
  },
  {
    path: '/my-applications',
    label: 'My applications',
    icon: FileText,
    roles: ['student'],
  },
  {
    path: '/my-internships',
    label: 'My internships',
    icon: Briefcase,
    roles: ['organization'],
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
    return '/my-internships';
  }
  if (role === 'admin') {
    return '/admin/users';
  }
  return '/account';
}
