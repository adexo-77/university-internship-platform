import { describe, expect, it } from 'vitest';
import { getHomePath, navigationItems, resolveBackTarget, resolveSectionTitle } from './navigation';

describe('Navigation Configuration', () => {
  it('returns /dashboard home path for every role', () => {
    expect(getHomePath('student')).toBe('/dashboard');
    expect(getHomePath('instructor')).toBe('/dashboard');
    expect(getHomePath('organization')).toBe('/dashboard');
    expect(getHomePath('admin')).toBe('/dashboard');
    expect(getHomePath('coordinator')).toBe('/dashboard');
  });

  it('has Dashboard as the first navigation item for all roles', () => {
    expect(navigationItems[0].label).toBe('Dashboard');
    expect(navigationItems[0].path).toBe('/dashboard');

    const roles = ['student', 'instructor', 'organization', 'admin', 'coordinator'] as const;
    for (const role of roles) {
      const items = navigationItems.filter((item) => !item.roles || item.roles.includes(role));
      expect(items[0].label).toBe('Dashboard');
      expect(items[0].path).toBe('/dashboard');
    }
  });

  it('filters navigation items for student role', () => {
    const studentItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('student')
    );
    const labels = studentItems.map((i) => i.label);

    expect(labels).toContain('Dashboard');
    expect(labels).toContain('Study plan');
    expect(labels).toContain('Courses');
    expect(labels).toContain('My courses');
    expect(labels).toContain('Internships');
    expect(labels).toContain('My applications');
    expect(labels).toContain('Profile');
    expect(labels).toContain('Account');
    expect(labels.indexOf('Study plan')).toBeGreaterThan(labels.indexOf('Dashboard'));
    expect(labels.indexOf('Study plan')).toBeLessThan(labels.indexOf('Courses'));
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('System status');
  });

  it('filters navigation items for instructor role', () => {
    const instructorItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('instructor')
    );
    const labels = instructorItems.map((i) => i.label);

    expect(labels).toContain('Dashboard');
    expect(labels).toContain('My courses');
    expect(labels).toContain('Account');
    expect(labels).not.toContain('Courses');
    expect(labels).not.toContain('Internships');
    expect(labels).not.toContain('My applications');
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('Profile');
    expect(labels).not.toContain('System status');
  });

  it('filters navigation items for organization role', () => {
    const orgItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('organization')
    );
    const labels = orgItems.map((i) => i.label);

    expect(labels).toContain('Dashboard');
    expect(labels).toContain('My internships');
    expect(labels).toContain('Profile');
    expect(labels).toContain('Account');
    expect(labels).not.toContain('Courses');
    expect(labels).not.toContain('Internships');
    expect(labels).not.toContain('My applications');
  });

  it('filters navigation items for admin role', () => {
    const adminItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('admin')
    );
    const labels = adminItems.map((i) => i.label);

    expect(labels).toContain('Dashboard');
    expect(labels).toContain('Users');
    expect(labels).toContain('Organizations');
    expect(labels).toContain('Internship reviews');
    expect(labels).toContain('Reports');
    expect(labels).toContain('Courses');
    expect(labels).toContain('Internships');
    expect(labels).toContain('Account');
    expect(labels).toContain('System status');
    expect(labels).not.toContain('My courses');
    expect(labels).not.toContain('My applications');
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('Profile');
  });

  it('filters navigation items for coordinator role', () => {
    const coordinatorItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('coordinator')
    );
    const labels = coordinatorItems.map((i) => i.label);

    expect(labels).toContain('Dashboard');
    expect(labels).toContain('Organizations');
    expect(labels).toContain('Internship reviews');
    expect(labels).toContain('Reports');
    expect(labels).toContain('Internships');
    expect(labels).toContain('Account');
    expect(labels).not.toContain('Users');
    expect(labels).not.toContain('Courses');
    expect(labels).not.toContain('System status');
    expect(labels).not.toContain('My courses');
    expect(labels).not.toContain('My applications');
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('Profile');
  });

  describe('resolveSectionTitle', () => {
    it('resolves dashboard for root and dashboard routes', () => {
      expect(resolveSectionTitle('/')).toBe('Dashboard');
      expect(resolveSectionTitle('/dashboard')).toBe('Dashboard');
    });

    it('resolves section titles for detail and nested routes instead of Dashboard', () => {
      expect(resolveSectionTitle('/courses/42')).toBe('Courses');
      expect(resolveSectionTitle('/courses/new')).toBe('Courses');
      expect(resolveSectionTitle('/courses/42/edit')).toBe('Courses');
      expect(resolveSectionTitle('/assignments/101')).toBe('Assignments');
      expect(resolveSectionTitle('/assignments/101/edit')).toBe('Assignments');
      expect(resolveSectionTitle('/internships/55')).toBe('Internships');
      expect(resolveSectionTitle('/internships/55/edit')).toBe('Internships');
      expect(resolveSectionTitle('/applications/88')).toBe('Applications');
      expect(resolveSectionTitle('/admin/users/new')).toBe('Users');
    });

    it('resolves independent sections matching prefixes correctly', () => {
      expect(resolveSectionTitle('/study-plan')).toBe('Study plan');
      expect(resolveSectionTitle('/my-courses')).toBe('My courses');
      expect(resolveSectionTitle('/my-applications')).toBe('My applications');
      expect(resolveSectionTitle('/my-internships')).toBe('My internships');
      expect(resolveSectionTitle('/notifications')).toBe('Notifications');
      expect(resolveSectionTitle('/account')).toBe('Account');
      expect(resolveSectionTitle('/profile')).toBe('Profile');
      expect(resolveSectionTitle('/status')).toBe('System status');
      expect(resolveSectionTitle('/admin/organizations')).toBe('Organizations');
      expect(resolveSectionTitle('/admin/internship-reviews')).toBe('Internship reviews');
      expect(resolveSectionTitle('/admin/reports')).toBe('Reports');
    });

    it('uses provided fallback when route is unknown', () => {
      expect(resolveSectionTitle('/unknown/subpage', 'Custom Fallback')).toBe('Custom Fallback');
      expect(resolveSectionTitle('/unknown/subpage')).toBe('Dashboard');
    });
  });

  describe('resolveBackTarget', () => {
    it('resolves correct parent targets for create and edit pages', () => {
      expect(resolveBackTarget('/courses/new')).toEqual({
        parentPath: '/courses',
        label: 'Back to Courses',
      });
      expect(resolveBackTarget('/courses/5/edit')).toEqual({
        parentPath: '/courses/5',
        label: 'Back to Course',
      });
      expect(resolveBackTarget('/courses/5/assignments/new')).toEqual({
        parentPath: '/courses/5',
        label: 'Back to Course',
      });
      expect(resolveBackTarget('/internships/new')).toEqual({
        parentPath: '/my-internships',
        label: 'Back to My Internships',
      });
      expect(resolveBackTarget('/admin/users/new')).toEqual({
        parentPath: '/admin/users',
        label: 'Back to Users',
      });
    });

    it('resolves correct parent targets for detail and grading pages', () => {
      expect(resolveBackTarget('/courses/12')).toEqual({
        parentPath: '/courses',
        label: 'Back to Courses',
      });
      expect(resolveBackTarget('/assignments/101')).toEqual({
        parentPath: '/courses',
        label: 'Back to Courses',
      });
      expect(resolveBackTarget('/assignments/101/submissions/7/grade')).toEqual({
        parentPath: '/assignments/101',
        label: 'Back to Assignment',
      });
      expect(resolveBackTarget('/study-plan')).toEqual({
        parentPath: '/dashboard',
        label: 'Back to Dashboard',
      });
      expect(resolveBackTarget('/notifications')).toEqual({
        parentPath: '/dashboard',
        label: 'Back to Dashboard',
      });
      expect(resolveBackTarget('/admin/reports')).toEqual({
        parentPath: '/dashboard',
        label: 'Back to Dashboard',
      });
    });

    it('returns null for top-level navigation routes without parent', () => {
      expect(resolveBackTarget('/dashboard')).toBeNull();
      expect(resolveBackTarget('/courses')).toBeNull();
      expect(resolveBackTarget('/internships')).toBeNull();
      expect(resolveBackTarget('/status')).toBeNull();
    });
  });
});
