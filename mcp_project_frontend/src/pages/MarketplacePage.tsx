import React, { useEffect, useState } from 'react';
import { templateApi } from '../services/api';

const MarketplacePage: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    templateApi.listTemplates()
      .then(res => {
        setTemplates(res.data.items || []);
      })
      .catch(err => {
        setError(err?.response?.data?.detail || 'Failed to load templates');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Marketplace</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Components</h2>
          <p className="text-gray-500">Browse our library of workflow components.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md col-span-2">
          <h2 className="text-xl font-semibold mb-4">Templates</h2>
          {loading && <p>Loading templates...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {!loading && !error && templates.length === 0 && <p className="text-gray-500">No templates found.</p>}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {templates.map((tpl) => (
              <div key={tpl.id} className="bg-neutral-50 dark:bg-neutral-800 rounded-lg shadow p-4 flex flex-col">
                <h3 className="font-semibold text-lg mb-2">{tpl.name}</h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{tpl.description}</p>
                <span className="text-xs text-neutral-400 mb-2">Category: {tpl.category || 'Uncategorized'}</span>
                <span className="text-xs text-neutral-400 mb-2">By: {tpl.created_by}</span>
                <span className="text-xs text-neutral-400 mb-2">{tpl.is_public ? 'Public' : 'Private'}</span>
                {/* TODO: Add preview and instantiate buttons */}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketplacePage;
