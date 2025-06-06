import { User } from '../types';

// Auth Context Types
export interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// Component Context Types
export interface ComponentState {
  components: any[];
  selectedComponent: any | null;
  loading: boolean;
  error: string | null;
}

// Theme Context Types
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

// Error Context Types
export interface ErrorState {
  hasError: boolean;
  message: string;
  type: 'error' | 'warning' | 'info';
  timestamp: Date;
}
