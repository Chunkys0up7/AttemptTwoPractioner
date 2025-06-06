import React, { createContext, ReactNode } from 'react';

export interface Theme {
  mode: 'light' | 'dark';
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
  };
  borderRadius: string;
  fontSize: string;
}

export const ThemeContext = createContext<Theme>({
  mode: 'light',
  colors: {
    primary: '#3B82F6',
    secondary: '#60A5FA',
    background: '#FFFFFF',
    text: '#1F2937'
  },
  borderRadius: '0.5rem',
  fontSize: '1rem'
});

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const theme: Theme = {
    mode: 'light',
    colors: {
      primary: '#3B82F6',
      secondary: '#60A5FA',
      background: '#FFFFFF',
      text: '#1F2937'
    },
    borderRadius: '0.5rem',
    fontSize: '1rem'
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
