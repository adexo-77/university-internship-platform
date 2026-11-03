import React, { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { navigationItems, NavItem, resolveSectionTitle } from '../../config/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useUnreadCount } from '../../hooks/useUnreadCount';
import { cn } from '../../lib/cn';
import { Badge, Brand, Button, IconButton } from '../ui';
import { NotificationBell } from '../notifications/NotificationBell';

export interface AppShellProps {
  children: React.ReactNode;
  navItems?: NavItem[];
  currentPath?: string;
  title?: string;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  navItems = navigationItems,
  currentPath,
  title,
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const drawerRef = useRef<HTMLElement>(null);
  const toggleButtonRef = useRef<HTMLButtonElement>(null);
  const location = useLocation();
  const { user, logout } = useAuth();
  const { unreadCount } = useUnreadCount({ enabled: Boolean(user) });

  const activePath = currentPath ?? location.pathname;

  // Filter navigation items based on user role
  const visibleNavItems = navItems.filter((item) => {
    if (!item.roles || item.roles.length === 0) {
      return true;
    }
    return user ? item.roles.includes(user.role) : false;
  });

  const topBarTitle = title ?? resolveSectionTitle(activePath, visibleNavItems[0]?.label);

  // Lock body scroll while mobile drawer is open
  useEffect(() => {
    if (!isMobileMenuOpen) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [isMobileMenuOpen]);

  // Handle Escape key and Tab focus trap inside drawer
  useEffect(() => {
    if (!isMobileMenuOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        setIsMobileMenuOpen(false);
        toggleButtonRef.current?.focus();
        return;
      }

      if (event.key === 'Tab' && drawerRef.current) {
        const focusables = drawerRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusables.length === 0) return;

        const firstElement = focusables[0];
        const lastElement = focusables[focusables.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMobileMenuOpen]);

  return (
    <div className="min-h-screen bg-chalk text-ink flex flex-col md:flex-row">
      {/* Mobile Top Navigation */}
      <div className="flex md:hidden items-center justify-between border-b border-line bg-surface px-4 py-3 pt-[calc(0.75rem+env(safe-area-inset-top,0px))]">
        <Link
          to="/"
          className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol rounded-control text-left"
        >
          <Brand size="sm" />
        </Link>
        <div className="flex items-center gap-2">
          {user && <NotificationBell count={unreadCount} />}
          <IconButton
            ref={toggleButtonRef}
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={isMobileMenuOpen}
            icon={isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          />
        </div>
      </div>

      {/* Sidebar Overlay on Mobile */}
      {isMobileMenuOpen && (
        <div
          role="presentation"
          aria-label="Close menu overlay"
          onClick={() => {
            setIsMobileMenuOpen(false);
            toggleButtonRef.current?.focus();
          }}
          className="fixed inset-0 z-40 bg-ink/40 md:hidden"
        />
      )}

      {/* Left Sidebar / Mobile Drawer */}
      <aside
        ref={drawerRef}
        aria-label="Navigation drawer"
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 border-r border-line bg-surface flex flex-col transition-transform duration-150 ease-in-out md:static md:translate-x-0 pt-[env(safe-area-inset-top,0px)] pb-[env(safe-area-inset-bottom,0px)]',
          isMobileMenuOpen ? 'translate-x-0 shadow-menu' : '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Platform Title */}
        <div className="border-b border-line px-5 py-4 flex items-center justify-between">
          <Link
            to="/"
            onClick={() => setIsMobileMenuOpen(false)}
            className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol rounded-control block text-left"
          >
            <Brand size="md" />
          </Link>
          <div className="md:hidden">
            <IconButton
              aria-label="Close menu drawer"
              icon={<X className="h-5 w-5" />}
              onClick={() => {
                setIsMobileMenuOpen(false);
                toggleButtonRef.current?.focus();
              }}
            />
          </div>
        </div>

        {/* Navigation */}
        <nav aria-label="Main navigation" className="flex-1 p-3 space-y-1 overflow-y-auto">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            const isExact = item.path === activePath;
            const isPrefix =
              item.path !== '/dashboard' &&
              item.path !== '/' &&
              activePath.startsWith(`${item.path}/`);
            const isActive = isExact || isPrefix;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsMobileMenuOpen(false)}
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'flex items-center gap-3 rounded-control px-3 py-2 text-base font-medium min-h-[44px] cursor-pointer transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol active:scale-[0.99]',
                  isActive
                    ? 'bg-petrol-tint text-petrol font-semibold'
                    : 'text-pencil hover:bg-chalk hover:text-ink active:bg-line'
                )}
              >
                <Icon className="h-4 w-4 shrink-0 text-current" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Mobile Sidebar Footer User Info */}
        {user && (
          <div className="border-t border-line p-3 md:hidden">
            <div className="px-3 py-1.5 text-xs text-pencil">
              Signed in as <span className="font-semibold text-ink">{user.full_name}</span> (
              {user.role})
            </div>
            <Button
              variant="quiet"
              size="sm"
              className="w-full justify-start text-brick hover:bg-chalk mt-1 min-h-[44px]"
              onClick={() => {
                setIsMobileMenuOpen(false);
                void logout();
              }}
            >
              Log out
            </Button>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Bar */}
        <header className="hidden md:flex h-14 items-center justify-between border-b border-line bg-surface px-8">
          <span className="text-base font-medium text-ink">{topBarTitle}</span>

          {user && (
            <div className="flex items-center gap-3">
              <NotificationBell count={unreadCount} />
              <span className="text-base text-ink font-medium">{user.full_name}</span>
              <Badge variant="neutral">{user.role}</Badge>
              <Button
                id="header-logout-button"
                variant="quiet"
                size="sm"
                onClick={() => void logout()}
              >
                Log out
              </Button>
            </div>
          )}
        </header>

        {/* Page Container */}
        <main className="flex-1 px-4 py-8 sm:px-8 max-w-5xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
