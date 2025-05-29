
import React, { createContext, useState, ReactNode, Dispatch, SetStateAction } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  setUser: Dispatch<SetStateAction<User | null>>;
  login: (userData: User) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    // Try to get user from local storage or default to a mock user
    const storedUser = localStorage.getItem('aiOpsUser');
    if (storedUser) {
      try {
        return JSON.parse(storedUser);
      } catch (error) {
        console.error("Failed to parse stored user:", error);
        localStorage.removeItem('aiOpsUser'); // Clear corrupted data
      }
    }
    // Default mock user if nothing in local storage or parsing fails
    return { 
        id: 'user123', 
        name: 'AI Ops User', 
        email: 'user@example.com', 
        avatarUrl: 'https://picsum.photos/seed/user123/100/100',
        role: 'Admin' 
    };
  });

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('aiOpsUser', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('aiOpsUser');
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};