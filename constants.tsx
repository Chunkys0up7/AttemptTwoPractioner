import React from 'react';
import { NavItem, AIComponent, Workflow, WorkflowRun, SystemStatus, WorkflowRunStatus, SpecificComponentType, AIComponentCostTier } from './types';
import {
  DashboardIcon, MarketplaceIcon, WorkflowBuilderIcon, ExecutionMonitorIcon, UploadIcon,
  LlmIcon, DataIcon, NotebookIcon, CubeIcon, DocumentTextIcon, RocketLaunchIcon, PlayIcon,
  CodeBracketIcon, PythonIcon, TypeScriptIcon, JupyterNotebookIcon, StreamlitIcon, MCPIcon, LLMAgentIcon
} from './icons';

export const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', name: 'Dashboard', icon: <DashboardIcon className="w-5 h-5" /> },
  { path: '/marketplace', name: 'Marketplace', icon: <MarketplaceIcon className="w-5 h-5" /> },
  { path: '/builder', name: 'Workflow Builder', icon: <WorkflowBuilderIcon className="w-5 h-5" /> },
  { path: '/monitor', name: 'Execution Monitor', icon: <ExecutionMonitorIcon className="w-5 h-5" /> },
  { path: '/submit-component', name: 'Submit Component', icon: <UploadIcon className="w-5 h-5" /> },
];

export const COMPONENT_TYPE_ICON_MAP: Record<SpecificComponentType, React.FC<React.SVGProps<SVGSVGElement>>> = {
  'LLM Prompt Agent': LLMAgentIcon,
  'Data': DataIcon,
  'Jupyter Notebook': JupyterNotebookIcon,
  'Python Script': PythonIcon,
  'TypeScript Script': TypeScriptIcon,
  'Streamlit App': StreamlitIcon,
  'MCP': MCPIcon,
  'Utility': CubeIcon,
  'Output': DocumentTextIcon,
};

export const DUMMY_COMPONENTS_PRESET: AIComponent[] = [
  { 
    id: 'comp1', name: 'GPT-4 Turbo Agent', type: 'LLM Prompt Agent', 
    description: 'Advanced LLM agent for complex text generation and reasoning tasks.', 
    version: '1.2.0', tags: ['LLM', 'OpenAI', 'Agent'], 
    icon: <LLMAgentIcon className="w-8 h-8 text-purple-500"/>, 
    compliance: ['SOC2'], costTier: 'High', visibility: 'Public',
    typeSpecificData: {
      llmPrompt: { model: 'gemini-2.5-flash-preview-04-17', systemPrompt: 'You are a helpful assistant.', temperature: 0.7, maxTokens: 1024 }
    }
  },
  { 
    id: 'comp2', name: 'Data Validator Script', type: 'Python Script', 
    description: 'Validates input data schemas and quality using Python.', 
    version: '2.0.1', tags: ['Python', 'Utility', 'Validation'], 
    icon: <PythonIcon className="w-8 h-8 text-blue-500"/>, 
    compliance: ['GDPR'], costTier: 'Low', visibility: 'Public',
    typeSpecificData: {
      codeContent: 'import pandas as pd\n\ndef validate(data):\n  # Basic validation logic\n  df = pd.DataFrame(data)\n  if df.empty:\n    return False, "Data is empty"\n  return True, "Data is valid"'
    }
  },
  { 
    id: 'comp5', name: 'Analysis Notebook', type: 'Jupyter Notebook', 
    description: 'Executes Jupyter notebooks for data analysis as part of a workflow.', 
    version: '1.5.0', tags: ['Notebook', 'Python', 'Analysis'], 
    icon: <JupyterNotebookIcon className="w-8 h-8 text-indigo-500"/>, 
    costTier: 'Low', visibility: 'Public',
    typeSpecificData: {
      notebookCells: [
        { id: 'cell1', type: 'markdown', content: '# Sales Data Analysis' },
        { id: 'cell2', type: 'code', content: 'import pandas as pd\nsales_data = pd.read_csv("sales.csv")\nprint(sales_data.describe())' }
      ]
    }
  },
  {
    id: 'comp7', name: 'Generic API Caller Utility', type: 'Utility',
    description: 'Calls any external HTTP API.', version: '1.0.0', tags: ['Utility', 'API'],
    icon: <CubeIcon className="w-8 h-8 text-gray-500" />, costTier: 'Free', visibility: 'Public'
  },
  {
    id: 'comp8', name: 'Text File Outputter', type: 'Output',
    description: 'Writes text content to a file.', version: '1.1.0', tags: ['Output', 'File'],
    icon: <DocumentTextIcon className="w-8 h-8 text-pink-500" />, costTier: 'Free', visibility: 'Public'
  },
  {
    id: 'comp9', name: 'Customer Churn Prediction App', type: 'Streamlit App',
    description: 'A Streamlit application for predicting customer churn.', version: '1.0.0', tags: ['Streamlit', 'Prediction', 'UI'],
    icon: <StreamlitIcon className="w-8 h-8 text-red-500" />, costTier: 'Medium', visibility: 'Public',
    typeSpecificData: {
      streamlitAppData: { gitRepoUrl: 'https://github.com/example/churn_app.git', mainScriptPath: 'app.py' }
    }
  },
  {
    id: 'comp10', name: 'Sentiment Analysis MCP', type: 'MCP',
    description: 'A Meta Component Package for performing sentiment analysis.', version: '1.0.0', tags: ['MCP', 'NLP', 'Sentiment'],
    icon: <MCPIcon className="w-8 h-8 text-green-500" />, costTier: 'Medium', visibility: 'Private',
    typeSpecificData: {
      mcpConfiguration: '{\n  "version": "1.0",\n  "components": [\n    {"id": "comp1", "name": "Text Input"},\n    {"id": "comp4", "name": "Sentiment Analyzer"}\n  ],\n  "connections": [\n    {"source": "comp1.output", "target": "comp4.input"}\n  ]\n}'
    }
  }
];

export const DUMMY_WORKFLOWS: Workflow[] = [
  { id: 'wf1', name: 'Customer Feedback Analysis', description: 'Analyzes customer reviews for sentiment and key topics.', status: 'Published', lastRun: new Date(Date.now() - 86400000 * 2).toISOString(), creator: 'Alice Wonderland', icon: <PlayIcon className="w-6 h-6 text-green-500" /> },
  { id: 'wf2', name: 'Daily Sales Report Generation', description: 'Generates and distributes daily sales reports.', status: 'Published', lastRun: new Date(Date.now() - 86400000).toISOString(), creator: 'Bob The Builder', icon: <PlayIcon className="w-6 h-6 text-green-500" /> },
  { id: 'wf3', name: 'Image Moderation Pipeline', description: 'Moderates uploaded images for inappropriate content.', status: 'Draft', creator: 'Carol Danvers', icon: <PlayIcon className="w-6 h-6 text-yellow-500" /> },
];

export const DUMMY_WORKFLOW_RUNS: WorkflowRun[] = [
  { id: 'run123', workflowName: 'Customer Feedback Analysis', status: WorkflowRunStatus.Success, startTime: new Date(Date.now() - 3600000 * 2).toISOString(), duration: '10min 15s', cost: '$0.53', initiator: 'Alice' },
  { id: 'run124', workflowName: 'Daily Sales Report Generation', status: WorkflowRunStatus.Running, startTime: new Date(Date.now() - 60000 * 5).toISOString(), duration: '5min 02s', cost: '$0.12', initiator: 'Scheduler' },
  { id: 'run125', workflowName: 'Image Moderation Pipeline', status: WorkflowRunStatus.Failed, startTime: new Date(Date.now() - 86400000).toISOString(), duration: '2min 30s', cost: '$0.05', initiator: 'Bob' },
  { id: 'run126', workflowName: 'Customer Feedback Analysis', status: WorkflowRunStatus.Aborted, startTime: new Date(Date.now() - 86400000 * 3).toISOString(), duration: '1min 00s', cost: '$0.01', initiator: 'Alice' },
  { id: 'run127', workflowName: 'Ad Hoc Data Processing', status: WorkflowRunStatus.Pending, startTime: new Date(Date.now() - 60000).toISOString(), initiator: 'Carol' },
];

export const DUMMY_SYSTEM_STATUS: SystemStatus[] = [
  { serviceName: 'API Gateway', status: 'OK' },
  { serviceName: 'Execution Runtime', status: 'OK' },
  { serviceName: 'Database Service', status: 'Warning', details: 'High latency on psql-replica-02' },
  { serviceName: 'Component Registry', status: 'OK' },
];

export const SUBMITTABLE_COMPONENT_TYPES: SpecificComponentType[] = [
  'Python Script', 'TypeScript Script', 'Jupyter Notebook', 'LLM Prompt Agent', 'Streamlit App', 'MCP',
  'Data', 'Utility', 'Output' // Keep general ones too for flexibility
];

export const ALL_COMPONENT_TYPES: SpecificComponentType[] = [...SUBMITTABLE_COMPONENT_TYPES];


export const COMPONENT_COMPLIANCE_OPTIONS = ['SOC2', 'GDPR', 'HIPAA', 'PCI DSS'];
export const COMPONENT_COST_TIERS: AIComponentCostTier[] = ['Free', 'Low', 'Medium', 'High'];
export const COMPONENT_VISIBILITY_OPTIONS: AIComponent['visibility'][] = ['Public', 'Private'];
export const LLM_MODELS = ['gemini-2.5-flash-preview-04-17', 'gpt-4', 'claude-3-opus']; // Example model list


export const AI_OPS_CONSOLE_LOGO = (
  <div className="flex items-center space-x-2 text-white">
    <RocketLaunchIcon className="w-8 h-8 text-primary" />
    <span className="text-xl font-semibold text-neutral-dark">AI Ops Console</span>
  </div>
);

/**
 * Key for storing custom components in localStorage.
 * @type {string}
 */
export const LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY = 'aiOpsCustomComponents';

/**
 * Default icon for AI components if specific one is not found.
 */
export const DEFAULT_COMPONENT_ICON = <CubeIcon className="w-8 h-8 text-gray-400" />;

/**
 * Gets the appropriate icon for a given component type.
 * @param {SpecificComponentType} type - The type of the component.
 * @param {React.SVGProps<SVGSVGElement>} [props] - Optional SVG props.
 * @returns {React.ReactElement} The icon component.
 */
export const getIconForComponentType = (type: SpecificComponentType, props?: React.SVGProps<SVGSVGElement>): React.ReactElement => {
  const IconComponent = COMPONENT_TYPE_ICON_MAP[type] || CubeIcon;
  return <IconComponent {...props} />;
};