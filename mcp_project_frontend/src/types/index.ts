import { ReactNode } from 'react';

export interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

export enum SpecificComponentType {
  Python = 'python',
  TypeScript = 'typescript',
  Notebook = 'notebook',
  Streamlit = 'streamlit',
  LLM = 'llm',
  Data = 'data'
}

export enum AIComponentCostTier {
  Low = 'low',
  Medium = 'medium',
  High = 'high'
}

export interface TypeSpecificData {
  python?: {
    requirements?: string[];
    dependencies?: string[];
  };
  typescript?: {
    dependencies?: string[];
    devDependencies?: string[];
  };
  notebook?: {
    cells?: NotebookCell[];
  };
  streamlit?: {
    requirements?: string[];
  };
  llm?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
  };
  data?: {
    format?: string;
    schema?: Record<string, any>;
  };
}

export interface NotebookCell {
  id: string;
  type: 'code' | 'markdown';
  content: string;
  output?: string;
}

export interface AIComponent {
  id: string;
  name: string;
  description: string;
  type: SpecificComponentType;
  typeSpecificData: TypeSpecificData;
  costTier: AIComponentCostTier;
  visibility: 'public' | 'private' | 'shared';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  inputs: Record<string, { type: string; description: string }>;
  outputs: Record<string, { type: string; description: string }>;
  configSchema: Record<string, any>;
  icon?: ReactNode;
  isCustom?: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  components: AIComponent[];
  status: 'active' | 'inactive' | 'draft';
  lastRun?: WorkflowRun;
  createdAt: Date;
  updatedAt: Date;
}

export enum WorkflowRunStatus {
  Pending = 'pending',
  Running = 'running',
  Completed = 'completed',
  Failed = 'failed',
  Cancelled = 'cancelled'
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: WorkflowRunStatus;
  startTime: Date;
  endTime?: Date;
  output?: any;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down';
  lastCheck: Date;
  components: {
    name: string;
    status: 'healthy' | 'degraded' | 'down';
    lastCheck: Date;
  }[];
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: string;
  role: string;
  createdAt?: Date;
  updatedAt?: Date;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  notifications: {
    email: boolean;
    push: boolean;
    in_app: boolean;
  };
  privacy: {
    data_collection: boolean;
    analytics: boolean;
    personalization: boolean;
  };
  display: {
    density: 'compact' | 'comfortable' | 'spacious';
    fontSize: 'small' | 'medium' | 'large';
    animations: boolean;
  };
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  severity: 'low' | 'medium' | 'high';
  read: boolean;
  createdAt: Date;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  severity: 'low' | 'medium' | 'high';
  createdAt: Date;
}

export interface RealTimeUpdate {
  id: string;
  type: string;
  data: any;
  timestamp: Date;
}

export interface DashboardMetric {
  name: string;
  value: number;
  unit: string;
  trend: number;
  timestamp: Date;
}

export interface CacheEntry<T> {
  value: T;
  timestamp: Date;
  ttl: number;
}

export interface PushSubscription {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
} 