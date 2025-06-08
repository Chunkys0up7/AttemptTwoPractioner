import React from 'react';
import { useNavigate } from 'react-router-dom';
import { EmptyState } from '../components/common/EmptyState';
import { DocumentTextIcon, CubeIcon } from '../components/common/icons';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Welcome to the Workflow Builder</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
          <p className="mb-4">Get started by creating your first workflow.</p>
          <button
            onClick={() => navigate('/workflows/new')}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create New Workflow
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Recent Workflows</h2>
          <EmptyState message="No workflows created yet." icon={<DocumentTextIcon className="w-12 h-12 text-neutral-300 mx-auto" />} />
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Components</h2>
          <EmptyState message="Browse our library of workflow components." icon={<CubeIcon className="w-12 h-12 text-neutral-300 mx-auto" />} />
          <button
            onClick={() => navigate('/components')}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mt-4"
          >
            View Components
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
