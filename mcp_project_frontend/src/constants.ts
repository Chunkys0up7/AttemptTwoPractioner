import { AIComponent, SpecificComponentType, AIComponentCostTier } from './types';
import React from 'react';
import StartIcon from '@components/icons/StartIcon';
import ProcessIcon from '@components/icons/ProcessIcon';
import EndIcon from '@components/icons/EndIcon';
import ConditionIcon from '@components/icons/ConditionIcon';
import DataIcon from '@components/icons/DataIcon';
import ActionIcon from '@components/icons/ActionIcon';
import DefaultIcon from '@components/icons/DefaultIcon';

// AI Ops Console Logo
export const AI_OPS_CONSOLE_LOGO = React.createElement('div', { className: 'flex items-center space-x-2' },
  React.createElement('h1', { className: 'text-2xl font-bold text-primary' }, 'AI Ops Console')
);

// Navigation items for the sidebar
export const NAV_ITEMS = [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: React.createElement(StartIcon, { className: 'w-5 h-5' })
  },
  {
    name: 'Marketplace',
    path: '/marketplace',
    icon: React.createElement(DataIcon, { className: 'w-5 h-5' })
  },
  {
    name: 'Workflow Builder',
    path: '/builder',
    icon: React.createElement(ProcessIcon, { className: 'w-5 h-5' })
  },
  {
    name: 'Execution Monitor',
    path: '/monitor',
    icon: React.createElement(ConditionIcon, { className: 'w-5 h-5' })
  },
  {
    name: 'Submit Component',
    path: '/submit-component',
    icon: React.createElement(ActionIcon, { className: 'w-5 h-5' })
  }
] as const;

// Define the icon component type
interface IconComponentProps {
  className?: string;
}

// Define the valid component types
export type ComponentType = 'start' | 'process' | 'end' | 'condition' | 'data' | 'action';

// Map of component types to their icons
const iconMap: Record<ComponentType, React.FC<IconComponentProps>> = {
  start: StartIcon,
  process: ProcessIcon,
  end: EndIcon,
  condition: ConditionIcon,
  data: DataIcon,
  action: ActionIcon,
};

export const DEFAULT_COMPONENT_ICON = DefaultIcon;

export const DUMMY_COMPONENTS_PRESET: AIComponent[] = [
  {
    id: 'start-node',
    name: 'Start Node',
    description: 'Start of the workflow',
    type: SpecificComponentType.Python as SpecificComponentType,
    typeSpecificData: {},
    costTier: AIComponentCostTier.Low,
    visibility: 'public',
    tags: ['start', 'workflow'],
    createdAt: new Date(),
    updatedAt: new Date(),
    inputs: {},
    outputs: {
      output: {
        type: 'any',
        description: 'Start signal',
      },
    },
    configSchema: {},
  },
  {
    id: 'process-node',
    name: 'Process Node',
    description: 'Process data or perform actions',
    type: SpecificComponentType.Python as SpecificComponentType,
    typeSpecificData: {},
    costTier: AIComponentCostTier.Low,
    visibility: 'public',
    tags: ['process', 'data'],
    createdAt: new Date(),
    updatedAt: new Date(),
    inputs: {
      input: {
        type: 'any',
        description: 'Input data',
      },
    },
    outputs: {
      output: {
        type: 'any',
        description: 'Processed data',
      },
    },
    configSchema: {
      properties: {
        name: {
          type: 'string',
          title: 'Name',
          default: 'Process',
        },
        description: {
          type: 'string',
          title: 'Description',
          default: 'Process data',
        },
      },
    },
  },
  {
    id: 'end-node',
    name: 'End Node',
    description: 'End of the workflow',
    type: SpecificComponentType.Python as SpecificComponentType,
    typeSpecificData: {},
    costTier: AIComponentCostTier.Low,
    visibility: 'public',
    tags: ['end', 'workflow'],
    createdAt: new Date(),
    updatedAt: new Date(),
    inputs: {
      input: {
        type: 'any',
        description: 'Final data',
      },
    },
    outputs: {},
    configSchema: {},
  },
];

export const LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY = 'customComponents';

export const getIconForComponentType = (type: ComponentType, className?: string): React.ReactNode => {
  const IconComponent = iconMap[type] || DefaultIcon;
  return IconComponent({ className });
};
