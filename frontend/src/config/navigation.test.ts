import { describe, expect, it } from 'vitest';
import { getHomePath, navigationItems } from './navigation';

describe('Navigation Configuration', () => {
  it('returns role-specific home paths', () => {
    expect(getHomePath('student')).toBe('/my-courses');
    expect(getHomePath('instructor')).toBe('/my-courses');
    expect(getHomePath('organization')).toBe('/profile');
    expect(getHomePath('admin')).toBe('/courses');
  });

  it('filters navigation items for student role', () => {
    const studentItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('student')
    );
    const labels = studentItems.map((i) => i.label);

    expect(labels).toContain('Courses');
    expect(labels).toContain('My courses');
    expect(labels).toContain('Profile');
    expect(labels).toContain('Account');
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
    expect(labels).not.toContain('Profile');
    expect(labels).not.toContain('System status');
  });

  it('filters navigation items for admin role', () => {
    const adminItems = navigationItems.filter(
      (item) => !item.roles || item.roles.includes('admin')
    );
    const labels = adminItems.map((i) => i.label);

    expect(labels).toContain('Courses');
    expect(labels).toContain('Account');
    expect(labels).toContain('System status');
    expect(labels).not.toContain('My courses');
    expect(labels).not.toContain('Profile');
  });
});
