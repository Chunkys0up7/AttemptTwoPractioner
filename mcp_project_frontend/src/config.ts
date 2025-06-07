// Environment configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const API_VERSION = 'v1';

// Component types
export const COMPONENT_TYPES = {
  LLM: 'LLM Prompt Agent',
  PYTHON: 'Python Script',
  NOTEBOOK: 'Jupyter Notebook',
  DATA: 'Data Processor',
  MODEL: 'Model Trainer',
  CUSTOM: 'Custom Component'
} as const;

// Cost tiers
export const COST_TIERS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high'
} as const;

// Visibility options
export const VISIBILITY_OPTIONS = {
  PUBLIC: 'public',
  PRIVATE: 'private'
} as const;

// Error messages
export const ERROR_MESSAGES = {
  FETCH_FAILED: 'Failed to fetch data from server',
  SAVE_FAILED: 'Failed to save data',
  DELETE_FAILED: 'Failed to delete item',
  UPDATE_FAILED: 'Failed to update item',
  INVALID_INPUT: 'Invalid input data',
  UNAUTHORIZED: 'Unauthorized access',
  NOT_FOUND: 'Resource not found'
} as const;

// Loading states
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
} as const;

// Theme settings
export const THEME = {
  COLORS: {
    PRIMARY: '#2563eb',
    SUCCESS: '#16a34a',
    ERROR: '#dc2626',
    WARNING: '#f59e0b',
    INFO: '#0ea5e9',
    BACKGROUND: '#f3f4f6',
    TEXT: '#1f2937'
  },
  SPACING: {
    SMALL: '4px',
    MEDIUM: '8px',
    LARGE: '16px',
    XLARGE: '24px'
  },
  TYPOGRAPHY: {
    HEADLINE: '24px',
    SUBHEAD: '18px',
    BODY: '16px',
    SMALL: '14px'
  }
} as const;

// Component constants
export const COMPONENT_CONSTANTS = {
  MAX_NAME_LENGTH: 50,
  MAX_DESCRIPTION_LENGTH: 200,
  MAX_TAGS: 10,
  MIN_TAG_LENGTH: 2,
  MAX_TAG_LENGTH: 20
} as const;

// Workflow constants
export const WORKFLOW_CONSTANTS = {
  MAX_STEPS: 50,
  MIN_STEP_DURATION: 1000,
  MAX_STEP_DURATION: 3600000
} as const;
