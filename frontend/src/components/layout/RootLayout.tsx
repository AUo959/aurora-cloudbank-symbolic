import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import {
  Code2,
  LayoutDashboard,
  Menu,
  MessageSquare,
  Network,
  Rocket,
  Shield,
  Sparkles,
  X,
} from 'lucide-react';
import { useRef, useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'AI Agent', href: '/agent', icon: MessageSquare },
  { name: 'Memory Network', href: '/memory', icon: Network },
  { name: 'Compliance', href: '/compliance', icon: Shield },
  { name: 'Orion Station', href: '/orion', icon: Rocket },
  { name: 'Simulations', href: '/simulations', icon: Sparkles },
  { name: 'Playground', href: '/playground', icon: Code2 },
];

export function RootLayout() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const mainContentRef = useRef<HTMLElement>(null);

  // Focus management for skip link
  const handleSkipToContent = () => {
    mainContentRef.current?.focus();
  };

  return (
    <div className="flex h-screen overflow-hidden aurora-gradient">
      {/* Skip to content link for accessibility */}
      <a
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          handleSkipToContent();
        }}
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-4 focus:left-4 focus:px-4 focus:py-2 focus:bg-primary-500 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-400"
      >
        Skip to main content
      </a>

      {/* Sidebar */}
      <aside
        className={cn(
          'flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-md transition-all duration-300',
          sidebarOpen ? 'w-64' : 'w-20'
        )}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4">
          {sidebarOpen && (
            <Link to="/" className="flex items-center space-x-2 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 focus:ring-offset-black/20 rounded-lg">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500">
                <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
              </div>
              <span className="text-xl font-display font-bold text-gradient">Aurora</span>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-white focus:ring-2 focus:ring-primary-400"
            aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            aria-expanded={sidebarOpen}
            title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {sidebarOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4" aria-label="Sidebar navigation">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-primary-400',
                  isActive
                    ? 'bg-primary-500/20 text-primary-400 quantum-glow'
                    : 'text-gray-400 hover:bg-white/10 hover:text-white'
                )}
                aria-current={isActive ? 'page' : undefined}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon
                  className={cn(
                    'h-5 w-5 shrink-0',
                    isActive ? 'text-primary-400' : 'text-gray-400 group-hover:text-white'
                  )}
                  aria-hidden="true"
                />
                {sidebarOpen ? (
                  <span className="ml-3">{item.name}</span>
                ) : (
                  <span className="sr-only">{item.name}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        {sidebarOpen && (
          <div className="border-t border-white/10 p-4">
            <div className="text-xs text-gray-500">
              <p className="font-mono">Aurora v1.0.0</p>
              <p className="mt-1">Complex Systems Platform</p>
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main
        id="main-content"
        ref={mainContentRef}
        tabIndex={-1}
        className="flex-1 overflow-y-auto focus:outline-none"
      >
        <Outlet />
      </main>
    </div>
  );
}
