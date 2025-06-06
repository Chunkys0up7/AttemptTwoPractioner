
import React from 'react';
import Card from '../common/Card';

// This is a placeholder. In a real app, this would be dynamic based on selected node.
interface PropertiesPanelProps {
  selectedNode?: any; // Replace 'any' with actual node type from React Flow
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ selectedNode }) => {
  return (
    <Card title="Properties" className="h-full">
      {selectedNode ? (
        <div>
          <h4 className="text-sm font-semibold text-neutral-700 mb-1">Node: {selectedNode.data?.name || selectedNode.id}</h4>
          <p className="text-xs text-neutral-500 mb-3">Type: {selectedNode.type}</p>
          
          {/* Example dynamic properties based on a simplified component structure */}
          {selectedNode.data?.config && Object.entries(selectedNode.data.config).map(([key, value]) => (
            <div key={key} className="mb-2">
              <label className="block text-xs font-medium text-neutral-600 mb-0.5">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</label>
              <input 
                type="text" 
                defaultValue={String(value)}
                className="block w-full text-xs p-1.5 border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:ring-primary focus:border-primary"
              />
            </div>
          ))}
          {/* Placeholder for more complex config UI */}
          {!selectedNode.data?.config && <p className="text-xs text-neutral-500">No configurable properties for this node type.</p>}

        </div>
      ) : (
        <p className="text-sm text-neutral-500">Select a node or edge to view its properties.</p>
      )}
      <div className="mt-4 p-3 bg-neutral-50 rounded-md">
         <h5 className="text-xs font-semibold text-neutral-600 mb-1">Workflow Settings</h5>
         <label className="block text-xs font-medium text-neutral-600 mb-0.5">Workflow Name</label>
         <input 
            type="text" 
            defaultValue="My New Workflow" 
            className="block w-full text-xs p-1.5 border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:ring-primary focus:border-primary"
        />
      </div>
    </Card>
  );
};

export default PropertiesPanel;