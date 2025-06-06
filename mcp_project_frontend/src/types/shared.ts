// Shared types for the application

// Component types
export interface Component {
  id: string;
  name: string;
  description: string;
  type: 'python' | 'typescript' | 'jupyter' | 'llm' | 'streamlit' | 'mcp';
  code?: string;
  config?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'developer' | 'user' | 'viewer';
  createdAt: string;
  updatedAt: string;
}

// Workflow types
export interface Workflow {
  id: string;
  name: string;
  description: string;
  components: Component[];
  connections: Connection[];
  createdAt: string;
  updatedAt: string;
}

// Connection types
export interface Connection {
  id: string;
  source: string;
  target: string;
  sourcePort: string;
  targetPort: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
}

// Authentication types
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

// Component Context types
export interface ComponentState {
  selectedComponent: Component | null;
  components: Component[];
  loading: boolean;
  error: string | null;
}

// UI types
export interface Theme {
  mode: 'light' | 'dark';
  colors: Record<string, string>;
  typography: Record<string, any>;
}

// Error types
export interface Error {
  message: string;
  code?: string;
  details?: any;
  timestamp: string;
}
