import React from 'react';
import { useNavigate } from 'react-router-dom';
import { EmptyState } from '../components/common/EmptyState';

const WorkflowsPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Workflows</h1>
        <button
          onClick={() => navigate('/workflows/new')}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          New Workflow
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <EmptyState message="No workflows created yet." />
      </div>
    </div>
  );
};

export default WorkflowsPage;
