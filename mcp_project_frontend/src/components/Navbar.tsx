import React from 'react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const handleNavClick = (path: string) => {
    // trackEvent('navigation_click', { path });
  };

  return (
    <nav className="bg-white dark:bg-neutral-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link
                to="/"
                onClick={() => handleNavClick('/')}
                className="text-xl font-bold text-primary"
              >
                AI Workflow Builder
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <Link
              to="/settings"
              onClick={() => handleNavClick('/settings')}
              className="text-neutral-600 dark:text-neutral-300 hover:text-primary dark:hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
            >
              Settings
            </Link>
          </div>
          <div className="flex items-center">
            <Link
              to="/help"
              onClick={() => handleNavClick('/help')}
              className="text-neutral-600 dark:text-neutral-300 hover:text-primary dark:hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
            >
              Help
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}; 