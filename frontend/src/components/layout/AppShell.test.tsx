import { fireEvent, render, screen } from '@testing-library/react';
import { Activity, BookOpen } from 'lucide-react';
import { describe, expect, it } from 'vitest';
import { AppShell } from './AppShell';

describe('AppShell Component', () => {
  it('renders default navigation item and page content', () => {
    render(
      <AppShell>
        <div>Page test content</div>
      </AppShell>
    );

    // Verifies navigation item from navigation configuration
    expect(screen.getByRole('link', { name: 'System status' })).toBeInTheDocument();
    expect(screen.getByText('Page test content')).toBeInTheDocument();

    // Verifies absence of placeholder/invented items and copy
    expect(screen.queryByText('Internships')).not.toBeInTheDocument();
    expect(screen.queryByText('Learning')).not.toBeInTheDocument();
    expect(screen.queryByText('Settings')).not.toBeInTheDocument();
    expect(screen.queryByText(/Academic term/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Platform environment/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Phase/i)).not.toBeInTheDocument();
  });

  it('renders custom navigation items passed via navItems prop', () => {
    const customNavItems = [
      { path: '/', label: 'System status', icon: Activity },
      { path: '/courses', label: 'Courses', icon: BookOpen },
    ];

    render(
      <AppShell navItems={customNavItems} currentPath="/courses">
        <div>Courses content</div>
      </AppShell>
    );

    expect(screen.getByRole('link', { name: 'System status' })).toBeInTheDocument();
    const coursesLink = screen.getByRole('link', { name: 'Courses' });
    expect(coursesLink).toBeInTheDocument();
    expect(coursesLink).toHaveAttribute('aria-current', 'page');
  });

  it('toggles mobile menu open and closed', () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );

    const toggleButton = screen.getByRole('button', { name: 'Open menu' });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(toggleButton);
    expect(screen.getByRole('button', { name: 'Close menu' })).toHaveAttribute(
      'aria-expanded',
      'true'
    );

    fireEvent.click(screen.getByRole('button', { name: 'Close menu' }));
    expect(screen.getByRole('button', { name: 'Open menu' })).toHaveAttribute(
      'aria-expanded',
      'false'
    );
  });
});
