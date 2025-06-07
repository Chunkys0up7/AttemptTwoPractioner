import type { JSONSchema7 } from 'json-schema';

export interface Compliance {
  id: string;
  name: string;
  description: string;
  category: string;
  requirements: string[];
  status: 'pending' | 'approved' | 'rejected';
};

export interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

export enum SpecificComponentType {
  LLM_PROMPT_AGENT = 'LLM Prompt Agent',
  PYTHON_SCRIPT = 'Python Script',
  JUPYTER_NOTEBOOK = 'Jupyter Notebook',
  DATA_PROCESSOR = 'Data Processor',
  MODEL_TRAINER = 'Model Trainer',
  CUSTOM = 'Custom Component'
};

export enum AIComponentCostTier {
  Low = 'low',
  Medium = 'medium',
  High = 'high'
}

export interface TypeSpecificData {
  python?: {
    requirements?: string[];
    dependencies?: string[];
    entryPoint?: string;
    environment?: string;
  };
  llm?: {
    provider?: string;
    model?: string;
    temperature?: number;
    maxTokens?: number;
    systemPrompt?: string;
  };
  notebook?: {
    cells: NotebookCell[];
    kernel?: string;
    language?: string;
  };
  data?: {
    format?: string;
    schema?: Record<string, any>;
    preprocessing?: string[];
    validation?: string[];
  };
  model?: {
    framework?: string;
    architecture?: string;
    hyperparameters?: Record<string, any>;
    metrics?: Record<string, any>;
  };
  custom?: {
    language?: string;
    runtime?: string;
    entryPoint?: string;
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
  type: SpecificComponentType;
  description: string;
  version: string;
  tags: string[];
  inputSchema: JSONSchema7;
  outputSchema: JSONSchema7;
  compliance: Compliance[];
  costTier: AIComponentCostTier;
  visibility: 'public' | 'private';
  isCustom: boolean;
  typeSpecificData: TypeSpecificData;
  createdAt: Date;
  updatedAt: Date;
  // Optional metadata
  author?: string;
  documentation?: string;
  exampleUsage?: string;
  dependencies?: string[];
  runtimeRequirements?: {
    cpu?: number;
    memory?: number;
    gpu?: boolean;
  };
  // Component state
  isSelected?: boolean;
  isLoading?: boolean;
  error?: string;
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