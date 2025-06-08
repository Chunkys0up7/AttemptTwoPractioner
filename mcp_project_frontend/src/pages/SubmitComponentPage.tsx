import React from 'react';
import { EmptyState } from '../components/common/EmptyState';
import { CubeIcon } from '../components/common/icons';

const SubmitComponentPage: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Submit Component</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <EmptyState message="Component submission interface will be implemented here." icon={<CubeIcon className="w-12 h-12 text-neutral-300 mx-auto" />} />
      </div>
    </div>
  );
};

export default SubmitComponentPage;
