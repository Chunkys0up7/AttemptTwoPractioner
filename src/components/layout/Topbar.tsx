import React, { useState } from 'react';
import { SearchIcon, BellIcon, UserCircleIcon, ChevronDownIcon, SunIcon, MoonIcon, DesktopComputerIcon } from '../../icons';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { theme, resolvedTheme, setTheme } = useTheme();

  const nextTheme = () => {
    if (theme === 'light') return setTheme('dark');
    if (theme === 'dark') return setTheme('system');
    return setTheme('light');
  };

  let icon = <SunIcon className="h-6 w-6" />;
  let label = 'Light';
  if (theme === 'dark' || (theme === 'system' && resolvedTheme === 'dark')) {
    icon = <MoonIcon className="h-6 w-6" />;
    label = 'Dark';
  } else if (theme === 'system') {
    icon = <DesktopComputerIcon className="h-6 w-6" />;
    label = 'System';
  }

  return (
    <button
      className="p-1 rounded-full text-neutral-500 hover:text-neutral-700 dark:text-neutral-300 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
      title={`Theme: ${label}`}
      onClick={nextTheme}
      aria-label="Toggle theme"
    >
      {icon}
    </button>
  );
};

const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="bg-white dark:bg-neutral-900 shadow-sm h-16 flex items-center justify-between px-6 sticky top-0 z-10 border-b border-neutral-200 dark:border-neutral-800">
      {/* Global Search */}
      <div className="relative w-1/3 lg:w-1/2">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 text-neutral-400 dark:text-neutral-500" />
        </div>
        <input
          type="text"
          placeholder="Search components, workflows, docs..."
          className="block w-full pl-10 pr-3 py-2 border border-neutral-300 dark:border-neutral-700 rounded-md leading-5 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm transition-colors"
        />
      </div>

      {/* Right side icons and user profile */}
      <div className="flex items-center space-x-5">
        <ThemeToggle />
        <button className="p-1 rounded-full text-neutral-500 hover:text-neutral-700 dark:text-neutral-300 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
          <BellIcon className="h-6 w-6" />
        </button>

        {user && (
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center space-x-2 focus:outline-none"
            >
              {user.avatarUrl ? (
                 <img src={user.avatarUrl} alt={user.name} className="h-8 w-8 rounded-full object-cover" />
              ) : (
                <UserCircleIcon className="h-8 w-8 text-neutral-500 dark:text-neutral-400" />
              )}
              <span className="hidden md:inline text-sm font-medium text-neutral-700 dark:text-neutral-200">{user.name}</span>
              <ChevronDownIcon className={`h-4 w-4 text-neutral-500 dark:text-neutral-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-neutral-900 rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-20 border border-neutral-200 dark:border-neutral-700">
                <a
                  href="#profile"
                  className="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  Your Profile
                </a>
                <a
                  href="#settings"
                  className="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  Settings
                </a>
                <button
                  onClick={() => { logout(); setDropdownOpen(false); }}
                  className="block w-full text-left px-4 py-2 text-sm text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Topbar; 