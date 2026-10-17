import React, { useState } from 'react';
import { Activity, BookOpen, Briefcase, Menu, Settings, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'System status', href: '#', active: true, icon: Activity },
    { name: 'Internships', href: '#', active: false, icon: Briefcase },
    { name: 'Learning', href: '#', active: false, icon: BookOpen },
    { name: 'Settings', href: '#', active: false, icon: Settings },
  ];

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
        {/* Academic Platform Identifier */}
        <div className="border-b border-line px-5 py-4">
          <span className="text-base font-semibold text-ink tracking-tight block">
            University Platform
          </span>
          <span className="text-xs text-pencil block mt-0.5">Academic workspace</span>
        </div>

        {/* Navigation */}
        <nav aria-label="Main navigation" className="flex-1 p-3 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.name}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                aria-current={item.active ? 'page' : undefined}
                className={cn(
                  'flex items-center gap-3 rounded-control px-3 py-2 text-base font-medium transition-colors duration-150',
                  item.active
                    ? 'bg-petrol-tint text-petrol font-semibold'
                    : 'text-pencil hover:bg-chalk hover:text-ink'
                )}
              >
                <Icon className="h-4 w-4 shrink-0 text-current" />
                <span>{item.name}</span>
              </a>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-line p-4 text-xs text-pencil">
          <span>Academic term 2026-2027</span>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Bar */}
        <header className="hidden md:flex h-14 items-center justify-between border-b border-line bg-surface px-8">
          <div className="text-xs text-pencil">
            Platform environment &bull;{' '}
            <span className="text-ink font-medium">Local workspace</span>
          </div>
          <div className="text-xs text-pencil">Phase 0b foundation</div>
        </header>

        {/* Page Container */}
        <main className="flex-1 px-4 py-8 sm:px-8 max-w-5xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
