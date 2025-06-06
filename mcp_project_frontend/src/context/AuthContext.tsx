
import React, { createContext, useState, ReactNode } from 'react';
import { User } from '../types';

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    // Try to get user from local storage
    const storedUser = localStorage.getItem('aiOpsUser');
    if (storedUser) {
      try {
        return JSON.parse(storedUser);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('aiOpsUser');
      }
    }
    return null;
  });

  const login = async (email: string, password: string): Promise<void> => {
    // TODO: Implement actual authentication logic
    if (!email || !password) {
      throw new Error('Email and password are required');
    }
    
    // Mock authentication - in production, this would make an API call
    if (email === 'test@example.com' && password === 'password123') {
      const mockUser: User = {
        id: '1',
        name: 'Test User',
        email: email,
        avatarUrl: '',
        role: 'user'
      };
      setUser(mockUser);
      localStorage.setItem('aiOpsUser', JSON.stringify(mockUser));
    } else {
      throw new Error('Invalid credentials');
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('aiOpsUser');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};