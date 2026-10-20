import { describe, expect, it } from 'vitest';
import { getHomePath, navigationItems } from './navigation';

describe('Navigation Configuration', () => {
  it('returns role-specific home paths', () => {
    expect(getHomePath('student')).toBe('/my-courses');
    expect(getHomePath('instructor')).toBe('/my-courses');
    expect(getHomePath('organization')).toBe('/my-internships');
    expect(getHomePath('admin')).toBe('/admin/users');
  });

  it('filters navigation items for student role', () => {
    const studentItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('student')
    );
    const labels = studentItems.map((i) => i.label);

    expect(labels).toContain('Courses');
    expect(labels).toContain('My courses');
    expect(labels).toContain('Internships');
    expect(labels).toContain('My applications');
    expect(labels).toContain('Profile');
    expect(labels).toContain('Account');
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('System status');
  });

  it('filters navigation items for instructor role', () => {
    const instructorItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('instructor')
    );
    const labels = instructorItems.map((i) => i.label);

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

    expect(labels).toContain('Users');
    expect(labels).toContain('Organizations');
    expect(labels).toContain('Courses');
    expect(labels).toContain('Internships');
    expect(labels).toContain('Account');
    expect(labels).toContain('System status');
    expect(labels).not.toContain('My courses');
    expect(labels).not.toContain('My applications');
    expect(labels).not.toContain('My internships');
    expect(labels).not.toContain('Profile');
  });
});
