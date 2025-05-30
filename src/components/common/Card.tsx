import React, { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  titleClassName?: string;
  actions?: ReactNode;
  onClick?: () => void;
  noPadding?: boolean;
}

const Card: React.FC<CardProps> = ({ children, className = '', title, titleClassName = '', actions, onClick, noPadding = false }) => {
  const baseClasses = "bg-white dark:bg-neutral-900 shadow-lg rounded-xl overflow-hidden transition-all duration-300 ease-in-out border border-neutral-200 dark:border-neutral-700";
  const clickableClasses = onClick ? "hover:shadow-xl cursor-pointer" : "";
  
  // Keyboard handler for accessibility
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      onClick();
    }
  };

  return (
    <div
      className={`${baseClasses} ${clickableClasses} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={onClick ? 'Card' : undefined}
      onKeyDown={onClick ? handleKeyDown : undefined}
    >
      {(title || actions) && (
        <div className={`flex justify-between items-center ${noPadding ? 'px-0 py-0' : 'px-5 py-4'} border-b border-neutral-200 dark:border-neutral-700`}> 
          {title && <h3 className={`text-lg font-semibold text-neutral-800 dark:text-neutral-100 ${titleClassName}`}>{title}</h3>}
          {actions && <div className="flex items-center space-x-2">{actions}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-5'}>
        {children}
      </div>
    </div>
  );
};

export default Card; 