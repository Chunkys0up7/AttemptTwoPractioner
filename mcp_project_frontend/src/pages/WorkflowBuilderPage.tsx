import React from 'react';
import { useLocation } from 'react-router-dom';

const WorkflowBuilderPage: React.FC = () => {
  const location = useLocation();
  const initialData = location.state?.workflowContent;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Workflow Builder</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        {initialData ? (
          <pre className="text-xs bg-neutral-100 rounded p-2 overflow-x-auto">
            {JSON.stringify(initialData, null, 2)}
          </pre>
        ) : (
          <div className="text-gray-500">Workflow builder interface will be implemented here.</div>
        )}
      </div>
    </div>
  );
};

export default WorkflowBuilderPage;
