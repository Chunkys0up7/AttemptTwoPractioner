import React from 'react';
import { ExclamationCircleIcon } from '../icons';

interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  return (
    <div className="flex items-center justify-center h-32">
      <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
        <ExclamationCircleIcon className="w-5 h-5" />
        <span>{message}</span>
      </div>
    </div>
  );
}; 