import { Activity, type LucideIcon } from 'lucide-react';

export interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
}

/**
 * Platform navigation items.
 * Only pages that exist are listed; future phases append their routes here.
 */
export const navigationItems: NavItem[] = [
  {
    path: '/',
    label: 'System status',
    icon: Activity,
  },
];
