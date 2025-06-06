import React from 'react';

const MarketplacePage: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Marketplace</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Components</h2>
          <p className="text-gray-500">Browse our library of workflow components.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Templates</h2>
          <p className="text-gray-500">Start with pre-built workflow templates.</p>
        </div>
      </div>
    </div>
  );
};

export default MarketplacePage;
