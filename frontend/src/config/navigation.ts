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
 * Central navigation configuration — no hard-coded items elsewhere.
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
    path: '/admin/reports',
    label: 'Reports',
    icon: FileText,
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
  { prefix: '/admin/reports', title: 'Reports' },
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

export interface BackTarget {
  parentPath: string;
  label: string;
}

/**
 * Resolves the parent route and back label for a nested page.
 * Returns null for top-level navigation routes that do not have a parent.
 */
export function resolveBackTarget(path: string): BackTarget | null {
  if (path === '/notifications') {
    return { parentPath: '/dashboard', label: 'Back to Dashboard' };
  }
  if (path === '/profile') {
    return { parentPath: '/dashboard', label: 'Back to Dashboard' };
  }
  if (path === '/account') {
    return { parentPath: '/dashboard', label: 'Back to Dashboard' };
  }
  if (path === '/admin/users/new') {
    return { parentPath: '/admin/users', label: 'Back to Users' };
  }
  if (path === '/admin/reports') {
    return { parentPath: '/dashboard', label: 'Back to Dashboard' };
  }
  if (path === '/courses/new') {
    return { parentPath: '/courses', label: 'Back to Courses' };
  }
  if (/^\/courses\/\d+\/edit$/.test(path)) {
    const courseId = path.split('/')[2];
    return { parentPath: `/courses/${courseId}`, label: 'Back to Course' };
  }
  if (/^\/courses\/\d+\/assignments\/new$/.test(path)) {
    const courseId = path.split('/')[2];
    return { parentPath: `/courses/${courseId}`, label: 'Back to Course' };
  }
  if (/^\/courses\/\d+$/.test(path)) {
    return { parentPath: '/courses', label: 'Back to Courses' };
  }
  if (/^\/assignments\/\d+\/edit$/.test(path)) {
    const assignmentId = path.split('/')[2];
    return { parentPath: `/assignments/${assignmentId}`, label: 'Back to Assignment' };
  }
  if (/^\/assignments\/\d+\/submissions\/\d+\/grade$/.test(path)) {
    const assignmentId = path.split('/')[2];
    return { parentPath: `/assignments/${assignmentId}`, label: 'Back to Assignment' };
  }
  if (/^\/assignments\/\d+$/.test(path)) {
    return { parentPath: '/courses', label: 'Back to Courses' };
  }
  if (path === '/internships/new') {
    return { parentPath: '/my-internships', label: 'Back to My Internships' };
  }
  if (/^\/internships\/\d+\/edit$/.test(path)) {
    const internshipId = path.split('/')[2];
    return { parentPath: `/internships/${internshipId}`, label: 'Back to Internship' };
  }
  if (/^\/internships\/\d+$/.test(path)) {
    return { parentPath: '/internships', label: 'Back to Internships' };
  }
  if (/^\/applications\/\d+$/.test(path)) {
    return { parentPath: '/my-internships', label: 'Back to My Internships' };
  }

  return null;
}
