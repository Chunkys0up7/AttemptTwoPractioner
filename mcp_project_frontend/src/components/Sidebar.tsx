import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAnalytics } from '../hooks/useAnalytics';

interface NavItem {
  path: string;
  label: string;
}

const navItems: NavItem[] = [
  { path: '/marketplace', label: 'Marketplace' },
  { path: '/workflow-builder', label: 'Workflow Builder' },
  { path: '/submit-component', label: 'Submit Component' }
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { trackEvent } = useAnalytics();

  const handleNavClick = (path: string) => {
    trackEvent('sidebar_navigation', { path });
  };

  return (
    <aside className="w-64 bg-white dark:bg-neutral-800 shadow-sm">
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => handleNavClick(item.path)}
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                location.pathname === item.path
                  ? 'bg-primary text-white'
                  : 'text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </aside>
  );
}; 