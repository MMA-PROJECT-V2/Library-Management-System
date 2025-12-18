import { NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  BookOpen,
  Library,
  Search,
  User,
  BookMarked,
  AlertTriangle,
  X
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  adminOnly?: boolean;
  librarianOrAdmin?: boolean;
}

const mainNavItems: NavItem[] = [
  { title: 'Dashboard', href: '/dashboard', icon: Home },
  { title: 'Browse Books', href: '/books', icon: BookOpen },
  { title: 'My Loans', href: '/my-loans', icon: Library },
  { title: 'Profile', href: '/profile', icon: User },
];

const adminNavItems: NavItem[] = [
  { title: 'Manage Books', href: '/admin/books', icon: BookMarked, librarianOrAdmin: true },
  { title: 'All Loans', href: '/admin/loans', icon: Library, librarianOrAdmin: true },
  { title: 'Overdue Loans', href: '/admin/overdue', icon: AlertTriangle, librarianOrAdmin: true },
];

export const Sidebar = ({ open, onClose }: SidebarProps) => {
  const { isLibrarianOrAdmin, isAdmin } = useAuth();
  const location = useLocation();

  const filteredAdminItems = adminNavItems.filter(item => {
    if (item.adminOnly) return isAdmin;
    if (item.librarianOrAdmin) return isLibrarianOrAdmin;
    return true;
  });

  const NavLinkItem = ({ item }: { item: NavItem }) => {
    const isActive = location.pathname === item.href;

    return (
      <NavLink
        to={item.href}
        onClick={onClose}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
          isActive
            ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-md"
            : "text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        )}
      >
        <item.icon className="h-5 w-5 flex-shrink-0" />
        <span>{item.title}</span>
        {item.badge !== undefined && item.badge > 0 && (
          <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-accent text-xs font-medium text-accent-foreground">
            {item.badge}
          </span>
        )}
      </NavLink>
    );
  };

  return (
    <>
      {/* Backdrop for mobile */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-full w-64 gradient-sidebar border-r border-sidebar-border transition-transform duration-300 md:sticky md:top-16 md:z-0 md:h-[calc(100vh-4rem)] md:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center justify-between px-4 md:hidden">
          <span className="font-display text-lg font-semibold text-sidebar-foreground">Menu</span>
          <Button variant="ghost" size="icon" onClick={onClose} className="text-sidebar-foreground hover:bg-sidebar-accent">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <ScrollArea className="h-[calc(100%-4rem)] md:h-full px-3 py-4">
          <nav className="flex flex-col gap-1">
            {mainNavItems.map((item) => (
              <NavLinkItem key={item.href} item={item} />
            ))}

            {filteredAdminItems.length > 0 && (
              <>
                <div className="my-4 border-t border-sidebar-border" />
                <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/50">
                  Administration
                </p>
                {filteredAdminItems.map((item) => (
                  <NavLinkItem key={item.href} item={item} />
                ))}
              </>
            )}
          </nav>
        </ScrollArea>
      </aside>
    </>
  );
};
