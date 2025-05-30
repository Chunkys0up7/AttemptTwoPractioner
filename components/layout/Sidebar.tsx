import React from 'react';
import { NavLink } from 'react-router-dom';
import { NavItem } from '../../types';
import { NAV_ITEMS, AI_OPS_CONSOLE_LOGO } from '../../constants';

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-neutral-dark dark:bg-neutral-950 flex flex-col h-screen fixed top-0 left-0 shadow-lg z-20 border-r border-neutral-800 dark:border-neutral-900">
      <div className="p-4 border-b border-neutral-700 dark:border-neutral-800">
        {AI_OPS_CONSOLE_LOGO}
      </div>
      <nav className="flex-grow p-4 space-y-2">
        {NAV_ITEMS.map((item: NavItem) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors duration-150 ease-in-out group
              ${isActive
                ? 'bg-primary text-white shadow-md'
                : 'text-neutral-300 dark:text-neutral-400 hover:bg-neutral-700 dark:hover:bg-neutral-800 hover:text-white dark:hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {React.isValidElement(item.icon) && React.cloneElement(
                  item.icon as React.ReactElement<React.SVGProps<SVGSVGElement>>,
                  {
                    className: `${(item.icon.props as React.SVGProps<SVGSVGElement>).className || ''} transition-colors duration-150 ease-in-out ${
                      isActive ? 'text-white' : 'text-neutral-400 dark:text-neutral-500 group-hover:text-white dark:group-hover:text-white'
                    }`.trim(),
                  }
                )}
                <span className="text-sm font-medium">{item.name}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-neutral-700 dark:border-neutral-800 text-xs text-neutral-500 dark:text-neutral-400">
        © {new Date().getFullYear()} AI Ops Console
      </div>
    </div>
  );
};

export default Sidebar;