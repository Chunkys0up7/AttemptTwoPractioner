import React from 'react';

export interface NavItem {
  path: string;
  name: string;
  icon: React.ReactNode;
}

/**
 * Defines the structure for a single cell within a Jupyter Notebook representation.
 */
export interface NotebookCell {
  id: string;
  type: 'code' | 'markdown';
  content: string;
}

/**
 * Represents the different types of AI components that can be created or used.
 */
export type SpecificComponentType = 
  | 'Python Script' 
  | 'TypeScript Script' 
  | 'Jupyter Notebook' 
  | 'LLM Prompt Agent' 
  | 'Streamlit App' 
  | 'MCP' // Meta Component Package
  | 'Data' // General data component
  | 'Utility' // General utility component
  | 'Output'; // General output component

export interface AIComponent {
  id: string;
  name: string;
  /** The primary type of the component, guiding its configuration and usage. */
  type: SpecificComponentType; 
  description: string;
  version: string;
  tags?: string[];
  icon?: React.ReactNode; // Could be a string key for predefined icons or SVG string
  inputSchema?: Record<string, any>; 
  outputSchema?: Record<string, any>; 
  compliance?: string[]; 
  costTier?: AIComponentCostTier;
  visibility: 'Public' | 'Private';
  isCustom?: boolean; // Flag to distinguish user-added components

  /** Data specific to the component's type, e.g., code for a script, cells for a notebook. */
  typeSpecificData?: {
    codeContent?: string; // For Python/TypeScript scripts
    notebookCells?: NotebookCell[]; // For Jupyter Notebooks
    llmPrompt?: { // For LLM Prompt Agents
      systemPrompt?: string;
      userPromptTemplate?: string;
      model?: string; // e.g., 'gemini-2.5-flash-preview-04-17'
      temperature?: number;
      maxTokens?: number;
      topP?: number;
      topK?: number;
    };
    streamlitAppData?: { // For Streamlit Apps
      gitRepoUrl?: string;
      mainScriptPath?: string; // e.g., app.py
      requirements?: string; // content of requirements.txt
    };
    mcpConfiguration?: string; // JSON or YAML string for MCP
    // Other type-specific fields can be added here
  };
}

export type AIComponentCostTier = 'Free' | 'Low' | 'Medium' | 'High';


export interface Workflow {
  id:string;
  name: string;
  description: string;
  status: 'Draft' | 'Published' | 'Archived';
  lastRun?: string; // ISO date string
  creator?: string;
  icon?: React.ReactNode;
}

export enum WorkflowRunStatus {
  Pending = 'Pending',
  Running = 'Running',
  Success = 'Success',
  Failed = 'Failed',
  Aborted = 'Aborted',
}

export interface WorkflowRun {
  id: string;
  workflowName: string;
  status: WorkflowRunStatus;
  startTime: string; // ISO date string
  duration?: string; // e.g., "10min", "5s"
  cost?: string; // e.g., "$0.50"
  initiator?: string;
}

export interface SystemStatus {
  serviceName: string;
  status: 'OK' | 'Warning' | 'Error';
  details?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  role: 'Admin' | 'Editor' | 'Viewer';
}

/**
 * Represents a message in the chat assistant.
 */
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}