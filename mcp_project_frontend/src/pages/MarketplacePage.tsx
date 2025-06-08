import React, { useEffect, useState } from 'react';
import { templateApi } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { EmptyState } from '../components/common/EmptyState';
import { SearchIcon } from '../components/common/icons';

const categories = [
  { label: 'All', value: '' },
  { label: 'Data', value: 'data' },
  { label: 'AI', value: 'ai' },
  { label: 'ETL', value: 'etl' },
  { label: 'Monitoring', value: 'monitoring' },
  // Add more categories as needed
];

const MarketplacePage: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [publicOnly, setPublicOnly] = useState(false);
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [instantiateLoading, setInstantiateLoading] = useState(false);
  const [instantiateError, setInstantiateError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchTemplates = () => {
    setLoading(true);
    setError(null);
    templateApi.listTemplates({
      search: search || undefined,
      category: category || undefined,
      public_only: publicOnly || undefined,
    })
      .then(res => {
        setTemplates(res.data.items || []);
      })
      .catch(err => {
        setError(err?.response?.data?.detail || 'Failed to load templates');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTemplates();
    // eslint-disable-next-line
  }, [search, category, publicOnly]);

  const openPreview = (id: string) => {
    setPreviewId(id);
    setPreviewLoading(true);
    setPreviewError(null);
    setPreviewData(null);
    templateApi.getTemplate(id)
      .then(res => {
        setPreviewData(res.data);
      })
      .catch(err => {
        setPreviewError(err?.response?.data?.detail || 'Failed to load template details');
      })
      .finally(() => setPreviewLoading(false));
  };

  const closePreview = () => {
    setPreviewId(null);
    setPreviewData(null);
    setPreviewError(null);
    setPreviewLoading(false);
  };

  const handleInstantiate = async () => {
    if (!previewId || !selectedVersion) return;
    setInstantiateLoading(true);
    setInstantiateError(null);
    try {
      // Fetch the selected version's content
      const res = await templateApi.getTemplate(previewId);
      const version = res.data.versions.find((v: any) => v.version === selectedVersion);
      if (!version) throw new Error('Version not found');
      // Navigate to /builder with workflow content as state
      navigate('/builder', { state: { workflowContent: version.content } });
      closePreview();
    } catch (err: any) {
      setInstantiateError(err?.response?.data?.detail || 'Failed to instantiate workflow');
    } finally {
      setInstantiateLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Marketplace</h1>
      <div className="mb-6 flex flex-wrap gap-4 items-end">
        <div>
          <label htmlFor="template-search" className="block text-sm font-medium mb-1">Search</label>
          <input
            id="template-search"
            type="text"
            className="border border-neutral-300 rounded-md px-3 py-2"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search templates..."
          />
        </div>
        <div>
          <label htmlFor="template-category" className="block text-sm font-medium mb-1">Category</label>
          <select
            id="template-category"
            className="border border-neutral-300 rounded-md px-3 py-2"
            value={category}
            onChange={e => setCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2 mt-6">
          <input
            id="public-only"
            type="checkbox"
            checked={publicOnly}
            onChange={e => setPublicOnly(e.target.checked)}
            className="accent-primary"
          />
          <label htmlFor="public-only" className="text-sm">Public Only</label>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Components</h2>
          <p className="text-gray-500">Browse our library of workflow components.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md col-span-2">
          <h2 className="text-xl font-semibold mb-4">Templates</h2>
          {loading && <p>Loading templates...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {!loading && !error && templates.length === 0 && (
            <EmptyState message="No Templates Found" icon={<SearchIcon className="w-16 h-16 text-neutral-300 mb-4" />}>
              <p className="text-neutral-500 mt-1">Try adjusting your search or filters.</p>
            </EmptyState>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {templates.map((tpl) => (
              <div
                key={tpl.id}
                className="bg-neutral-50 dark:bg-neutral-800 rounded-lg shadow p-4 flex flex-col cursor-pointer hover:ring-2 hover:ring-primary"
                tabIndex={0}
                role="button"
                aria-label={`Preview template ${tpl.name}`}
                onClick={() => openPreview(tpl.id)}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') openPreview(tpl.id); }}
              >
                <h3 className="font-semibold text-lg mb-2">{tpl.name}</h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{tpl.description}</p>
                <span className="text-xs text-neutral-400 mb-2">Category: {tpl.category || 'Uncategorized'}</span>
                <span className="text-xs text-neutral-400 mb-2">By: {tpl.created_by}</span>
                <span className="text-xs text-neutral-400 mb-2">{tpl.is_public ? 'Public' : 'Private'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Template Preview Modal */}
      {previewId && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
          role="dialog"
          aria-modal="true"
          aria-label="Template Preview"
        >
          <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg max-w-lg w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
              aria-label="Close template preview"
              onClick={closePreview}
            >
              <span aria-hidden="true">&times;</span>
            </button>
            <h2 className="text-xl font-semibold mb-4">Template Preview</h2>
            {previewLoading && <p>Loading template details...</p>}
            {previewError && <p className="text-red-500">{previewError}</p>}
            {previewData && (
              <div>
                <h3 className="font-semibold text-lg mb-2">{previewData.name}</h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{previewData.description}</p>
                <span className="text-xs text-neutral-400 mb-2">Category: {previewData.category || 'Uncategorized'}</span>
                <span className="text-xs text-neutral-400 mb-2">By: {previewData.created_by}</span>
                <span className="text-xs text-neutral-400 mb-2">{previewData.is_public ? 'Public' : 'Private'}</span>
                {/* Metadata and versions */}
                {previewData.template_metadata && (
                  <div className="mt-2">
                    <h4 className="font-semibold text-sm mb-1">Metadata</h4>
                    <pre className="bg-neutral-100 dark:bg-neutral-900 rounded p-2 text-xs overflow-x-auto">
                      {JSON.stringify(previewData.template_metadata, null, 2)}
                    </pre>
                  </div>
                )}
                {previewData.versions && previewData.versions.length > 0 && (
                  <div className="mt-2">
                    <h4 className="font-semibold text-sm mb-1">Versions</h4>
                    <select
                      className="border border-neutral-300 rounded-md px-2 py-1 mb-2"
                      value={selectedVersion ?? previewData.versions[0].version}
                      onChange={e => setSelectedVersion(Number(e.target.value))}
                    >
                      {previewData.versions.map((v: any) => (
                        <option key={v.id} value={v.version}>
                          v{v.version} - {v.created_at ? new Date(v.created_at).toLocaleString() : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <button
                  className="mt-4 px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark disabled:opacity-50"
                  onClick={handleInstantiate}
                  disabled={instantiateLoading || !selectedVersion}
                  aria-label="Instantiate workflow from template"
                >
                  {instantiateLoading ? 'Instantiating...' : 'Instantiate'}
                </button>
                {instantiateError && <p className="text-red-500 mt-2">{instantiateError}</p>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketplacePage;
