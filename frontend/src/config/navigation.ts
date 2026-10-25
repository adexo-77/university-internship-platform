import {
  Activity,
  BookMarked,
  BookOpen,
  Briefcase,
  Building2,
  ClipboardCheck,
  Contact,
  FileText,
  LayoutDashboard,
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
    path: '/dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
  },
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
    roles: ['admin', 'coordinator'],
  },
  {
    path: '/admin/internship-reviews',
    label: 'Internship reviews',
    icon: ClipboardCheck,
    roles: ['admin', 'coordinator'],
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
    roles: ['student', 'admin', 'coordinator'],
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

export const SECTION_ROUTES: Array<{ prefix: string; title: string }> = [
  { prefix: '/dashboard', title: 'Dashboard' },
  { prefix: '/notifications', title: 'Notifications' },
  { prefix: '/account', title: 'Account' },
  { prefix: '/profile', title: 'Profile' },
  { prefix: '/status', title: 'System status' },
  { prefix: '/admin/users', title: 'Users' },
  { prefix: '/admin/organizations', title: 'Organizations' },
  { prefix: '/admin/internship-reviews', title: 'Internship reviews' },
  { prefix: '/my-courses', title: 'My courses' },
  { prefix: '/my-applications', title: 'My applications' },
  { prefix: '/my-internships', title: 'My internships' },
  { prefix: '/courses', title: 'Courses' },
  { prefix: '/assignments', title: 'Assignments' },
  { prefix: '/internships', title: 'Internships' },
  { prefix: '/applications', title: 'Applications' },
];

/**
 * Resolves the top bar section/page title from a URL path.
 * Avoids falling back to "Dashboard" on detail and nested routes.
 */
export function resolveSectionTitle(path: string, fallback?: string): string {
  if (path === '/' || path === '') {
    return 'Dashboard';
  }

  const match = SECTION_ROUTES.find(
    (route) => path === route.prefix || path.startsWith(`${route.prefix}/`)
  );
  if (match) {
    return match.title;
  }

  return fallback ?? 'Dashboard';
}

/**
 * Returns the default home path for a given user role.
 */
export function getHomePath(role?: UserRole): string {
  if (role) {
    return '/dashboard';
  }
  return '/dashboard';
}
