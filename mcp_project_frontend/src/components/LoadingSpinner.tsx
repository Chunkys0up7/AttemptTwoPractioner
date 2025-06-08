import React from 'react';
import { cn } from '../utils/cn';

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'neutral' | 'white';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  className,
  size = 'md',
  color = 'primary',
  ...props
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };
  const colorClasses = {
    primary: 'text-primary',
    neutral: 'text-neutral-400',
    white: 'text-white',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center',
        className
      )}
      role="status"
      aria-label="Loading"
      aria-live="polite"
      {...props}
    >
      <span
        className={cn(
          'animate-spin rounded-full border-2 border-current border-t-transparent',
          sizeClasses[size],
          colorClasses[color]
        )}
        aria-hidden="true"
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
}; 