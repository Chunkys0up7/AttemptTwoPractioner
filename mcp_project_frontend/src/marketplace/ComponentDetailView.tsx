import React from 'react';
import { AIComponent } from '../../types';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { CodeBracketIcon, TableCellsIcon, PlusIcon, CubeIcon } from '../../icons';

interface ComponentDetailViewProps {
  component: AIComponent | null;
  isOpen: boolean;
  onClose: () => void;
}

const DetailSection: React.FC<{
  title: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
}> = ({ title, children, icon }) => {
  let sectionIconDisplay: React.ReactNode = null;
  if (icon && React.isValidElement(icon)) {
    sectionIconDisplay = React.cloneElement(
      icon as React.ReactElement<React.SVGProps<SVGSVGElement>>,
      { className: 'w-5 h-5 mr-2 text-primary' }
    );
  }

  return (
    <div className="py-4 border-b border-neutral-200 last:border-b-0">
      <h4 className="text-md font-semibold text-neutral-700 mb-3 flex items-center">
        {sectionIconDisplay}
        {title}
      </h4>
      <div className="text-sm text-neutral-600 bg-neutral-50 p-4 rounded-lg">{children}</div>
    </div>
  );
};

const ComponentDetailView: React.FC<ComponentDetailViewProps> = ({
  component,
  isOpen,
  onClose,
}) => {
  if (!component) return null;

  let mainIconDisplay: React.ReactNode = null;
  if (component.icon && React.isValidElement(component.icon)) {
    mainIconDisplay = React.cloneElement(
      component.icon as React.ReactElement<React.SVGProps<SVGSVGElement>>,
      { className: 'w-16 h-16 text-primary' }
    );
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={component.name} size="xl">
      <div className="space-y-6">
        <div className="flex items-start space-x-6 p-4 bg-neutral-50 rounded-lg">
          <div className="flex-shrink-0">{mainIconDisplay}</div>
          <div className="min-w-0 flex-1">
            <p className="text-sm text-neutral-500">
              Version {component.version} - Type:{' '}
              <span className="font-semibold text-indigo-600">{component.type}</span>
            </p>
            <p className="mt-2 text-neutral-700">{component.description}</p>
          </div>
        </div>

        {component.tags && component.tags.length > 0 && (
          <DetailSection title="Tags" icon={<CubeIcon />}>
            <div className="flex flex-wrap gap-2">
              {component.tags.map(tag => (
                <span
                  key={tag}
                  className="px-2.5 py-1 bg-primary/10 text-primary text-xs font-medium rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </DetailSection>
        )}

        {component.compliance && component.compliance.length > 0 && (
          <DetailSection title="Compliance" icon={<CubeIcon />}>
            <div className="flex flex-wrap gap-2">
              {component.compliance.map(c => (
                <span
                  key={c}
                  className="px-2.5 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full"
                >
                  {c}
                </span>
              ))}
            </div>
          </DetailSection>
        )}

        {component.costTier && (
          <DetailSection title="Cost Tier" icon={<CubeIcon />}>
            <span className="px-2.5 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full">
              {component.costTier}
            </span>
          </DetailSection>
        )}

        {component.inputSchema && (
          <DetailSection title="Input Schema" icon={<CodeBracketIcon />}>
            <pre className="bg-neutral-800 text-neutral-100 p-4 rounded-md text-xs overflow-x-auto max-h-40">
              {JSON.stringify(component.inputSchema, null, 2)}
            </pre>
          </DetailSection>
        )}

        {component.outputSchema && (
          <DetailSection title="Output Schema" icon={<TableCellsIcon />}>
            <pre className="bg-neutral-800 text-neutral-100 p-4 rounded-md text-xs overflow-x-auto max-h-40">
              {JSON.stringify(component.outputSchema, null, 2)}
            </pre>
          </DetailSection>
        )}

        <DetailSection title="Sandbox & Testing" icon={<CubeIcon />}>
          <div className="space-y-3">
            <p className="text-neutral-600">
              Isolated testing environment for this component. (Preview)
            </p>
            <Button variant="secondary" size="sm">
              Test in Sandbox
            </Button>
          </div>
        </DetailSection>

        <DetailSection title="Dependencies" icon={<CubeIcon />}>
          <p className="text-neutral-600">
            Component relationships and dependencies. (Visualizer Preview)
          </p>
        </DetailSection>
      </div>
      <div className="mt-6 pt-4 border-t border-neutral-200 flex justify-end space-x-3">
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
        <Button variant="primary" leftIcon={<PlusIcon className="w-4 h-4" />}>
          Add to Workflow
        </Button>
      </div>
    </Modal>
  );
};

export default ComponentDetailView;
