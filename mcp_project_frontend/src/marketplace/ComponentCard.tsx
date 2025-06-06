import React from 'react';
import { AIComponent } from '../../types';
import Card from '../common/Card';
import Button from '../common/Button';
import { EyeIcon } from '../../icons';
// Link removed as it's not used directly in this component after changes, but kept for context if needed elsewhere
// import { Link } from 'react-router-dom';

interface ComponentCardProps {
  component: AIComponent;
  onSelect: (component: AIComponent) => void;
}

const ComponentCard: React.FC<ComponentCardProps> = ({ component, onSelect }) => {
  const defaultIcon = (
    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary text-2xl font-bold">
      {component.name.substring(0, 1)}
    </div>
  );

  let iconDisplay: React.ReactNode;
  if (component.icon && React.isValidElement(component.icon)) {
    iconDisplay = React.cloneElement(
      component.icon as React.ReactElement<React.SVGProps<SVGSVGElement>>,
      { className: 'w-12 h-12 text-primary' }
    );
  } else {
    iconDisplay = defaultIcon;
  }

  return (
    <Card className="flex flex-col h-full transform hover:scale-105 transition-transform duration-200 ease-out hover:shadow-lg">
      <div className="flex items-center space-x-4 mb-4 p-4 border-b border-neutral-200">
        <div className="flex-shrink-0">{iconDisplay}</div>
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-neutral-800 truncate" title={component.name}>
            {component.name}
          </h3>
          <p className="text-xs text-neutral-500">
            v{component.version} -{' '}
            <span className="font-medium text-indigo-600">{component.type}</span>
          </p>
        </div>
      </div>

      <div className="flex-1 px-4">
        <p className="text-sm text-neutral-600 mb-4 line-clamp-3">{component.description}</p>

        {component.tags && component.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1.5">
              {component.tags.slice(0, 3).map(tag => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-neutral-100 text-neutral-700 rounded-full text-xs font-medium"
                >
                  {tag}
                </span>
              ))}
              {component.tags.length > 3 && (
                <span className="px-2 py-0.5 bg-neutral-100 text-neutral-700 rounded-full text-xs font-medium">
                  +{component.tags.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="mt-auto p-4 border-t border-neutral-200 bg-neutral-50">
        <Button
          variant="primary"
          size="sm"
          onClick={() => onSelect(component)}
          className="w-full"
          leftIcon={<EyeIcon className="w-4 h-4" />}
        >
          View Details
        </Button>
      </div>
    </Card>
  );
};

export default ComponentCard;
