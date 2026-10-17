import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { navigationItems, NavItem } from '../../config/navigation';
import { cn } from '../../lib/utils';

export interface AppShellProps {
  children: React.ReactNode;
  navItems?: NavItem[];
  currentPath?: string;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  navItems = navigationItems,
  currentPath = '/',
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const activeItem = navItems.find((item) => item.path === currentPath) ?? navItems[0];

  return (
    <div className="min-h-screen bg-chalk text-ink flex flex-col md:flex-row">
      {/* Mobile Top Navigation */}
      <div className="flex md:hidden items-center justify-between border-b border-line bg-surface px-4 py-3">
        <span className="font-semibold text-ink text-base">University Platform</span>
        <button
          type="button"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMobileMenuOpen}
          className="rounded-control border border-line p-1.5 text-pencil hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol"
        >
          {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Sidebar Overlay on Mobile */}
      {isMobileMenuOpen && (
        <div
          role="presentation"
          onClick={() => setIsMobileMenuOpen(false)}
          className="fixed inset-0 z-40 bg-ink/20 md:hidden"
        />
      )}

      {/* Left Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 border-r border-line bg-surface flex flex-col transition-transform duration-150 ease-in-out md:static md:translate-x-0',
          isMobileMenuOpen ? 'translate-x-0 shadow-menu' : '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Platform Title */}
        <div className="border-b border-line px-5 py-4">
          <span className="text-base font-semibold text-ink tracking-tight block">
            University Platform
          </span>
        </div>

        {/* Navigation */}
        <nav aria-label="Main navigation" className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.path === currentPath;

            return (
              <a
                key={item.path}
                href={item.path}
                onClick={() => setIsMobileMenuOpen(false)}
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'flex items-center gap-3 rounded-control px-3 py-2 text-base font-medium transition-colors duration-150',
                  isActive
                    ? 'bg-petrol-tint text-petrol font-semibold'
                    : 'text-pencil hover:bg-chalk hover:text-ink'
                )}
              >
                <Icon className="h-4 w-4 shrink-0 text-current" />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Bar */}
        <header className="hidden md:flex h-14 items-center border-b border-line bg-surface px-8">
          <span className="text-base font-medium text-ink">{activeItem?.label}</span>
        </header>

        {/* Page Container */}
        <main className="flex-1 px-4 py-8 sm:px-8 max-w-5xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
