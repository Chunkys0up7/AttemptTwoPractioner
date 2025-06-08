import React from 'react';

interface EmptyStateProps {
  message: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ message, icon, children, className }) => {
  return (
    <div className={`flex flex-col items-center justify-center py-10 text-center ${className || ''}`.trim()} role="status" aria-live="polite">
      {icon && <div className="mb-4">{icon}</div>}
      <h3 className="text-xl font-semibold text-neutral-700 dark:text-neutral-200">{message}</h3>
      {children && <div className="mt-2">{children}</div>}
    </div>
  );
}; 