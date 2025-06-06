import React from 'react';
import { AIComponent } from '../types/components';

interface ComponentCardProps {
  component: AIComponent;
  onSelect: () => void;
}

export const ComponentCard: React.FC<ComponentCardProps> = ({ component, onSelect }) => {
  return (
    <div
      className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer p-4"
      onClick={onSelect}
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
          <span className="text-lg font-semibold text-primary">
            {component.name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-neutral-800 dark:text-neutral-100 line-clamp-1">
            {component.name}
          </h3>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1 line-clamp-2">
            {component.description}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="inline-block bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 px-2 py-0.5 rounded-full text-xs font-medium">
              {component.type}
            </span>
            {component.tags.map(tag => (
              <span
                key={tag}
                className="inline-block bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300 px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {tag}
              </span>
            ))}
          </div>
          <div className="mt-3 flex items-center justify-between text-sm text-neutral-500 dark:text-neutral-400">
            <span>v{component.version}</span>
            <span>By {component.author}</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 