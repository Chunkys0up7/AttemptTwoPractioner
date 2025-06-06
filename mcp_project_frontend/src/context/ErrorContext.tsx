import React, { createContext, useState, ReactNode } from 'react';

export interface ErrorState {
  hasError: boolean;
  message: string;
  type: 'error' | 'warning' | 'info';
  timestamp: Date;
}

export const ErrorContext = createContext<ErrorState>({
  hasError: false,
  message: '',
  type: 'info',
  timestamp: new Date()
});

interface ErrorProviderProps {
  children: ReactNode;
}

export const ErrorProvider: React.FC<ErrorProviderProps> = ({ children }) => {
  const [error, setError] = useState<ErrorState>({
    hasError: false,
    message: '',
    type: 'info',
    timestamp: new Date()
  });

  return (
    <ErrorContext.Provider value={error}>
      {children}
    </ErrorContext.Provider>
  );
};
