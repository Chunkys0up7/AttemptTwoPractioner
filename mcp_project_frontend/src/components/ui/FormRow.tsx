import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export interface FormRowProps extends React.HTMLAttributes<HTMLDivElement> {
  label?: string;
  htmlFor?: string;
  error?: string;
  required?: boolean;
  helperText?: string;
  children: React.ReactNode;
}

const FormRow = forwardRef<HTMLDivElement, FormRowProps>(
  ({ label, htmlFor, error, required, helperText, children, className, ...props }, ref) => {
    return (
      <div className={cn('mb-4', className)} ref={ref} {...props}>
        {label && (
          <label htmlFor={htmlFor} className="block text-sm font-medium mb-1">
            {label} {required && <span className="text-red-500">*</span>}
          </label>
        )}
        {children}
        {helperText && !error && (
          <p className="text-xs text-muted-foreground mt-1">{helperText}</p>
        )}
        {error && (
          <p className="text-xs text-destructive mt-1" role="alert">{error}</p>
        )}
      </div>
    );
  }
);

FormRow.displayName = 'FormRow';

export { FormRow }; 