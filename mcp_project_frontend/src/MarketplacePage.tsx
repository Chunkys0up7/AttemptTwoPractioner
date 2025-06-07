import React, { useState, useMemo, useEffect } from 'react';
import ComponentCard from '../components/marketplace/ComponentCard';
import FilterPanel from '../components/marketplace/FilterPanel';
import ComponentDetailView from '../components/marketplace/ComponentDetailView';
import { AIComponent } from '../types';
import { SearchIcon } from '../icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useComponents } from '@context/ComponentContext'; // Import useComponents


const MarketplacePage: React.FC = () => {
  const { allComponents, getComponentById } = useComponents(); // Use context
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<Record<string, any>>({
    type: [],
    compliance: [],
    costTier: [],
  });
  const [selectedComponent, setSelectedComponent] = useState<AIComponent | null>(null);
  const { componentId } = useParams<{ componentId?: string }>();
  const navigate = useNavigate();


  useEffect(() => {
    if (componentId) {
      const component = getComponentById(componentId); // Use getComponentById from context
      if (component) {
        setSelectedComponent(component);
      } else {
        // Optionally navigate back or show not found if ID is invalid
        navigate('/marketplace', { replace: true });
      }
    } else {
      setSelectedComponent(null); // Close modal if no ID in URL
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [componentId, getComponentById]); // Added getComponentById to dependencies


  const handleFilterChange = (filterName: string, value: any) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  };

  const handleComponentSelect = (component: AIComponent) => {
    setSelectedComponent(component);
    navigate(`/marketplace/component/${component.id}`);
  };
  
  const handleCloseDetailView = () => {
    setSelectedComponent(null);
    navigate('/marketplace');
  };

  const filteredComponents = useMemo(() => {
    return allComponents.filter(component => { // Use allComponents from context
      const searchMatch = component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          component.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (component.tags && component.tags.join(' ').toLowerCase().includes(searchTerm.toLowerCase()));
      
      const typeMatch = filters.type.length === 0 || filters.type.includes(component.type);
      const complianceMatch = filters.compliance.length === 0 || (component.compliance && component.compliance.some((c: string) => filters.compliance.includes(c)));
      const costMatch = filters.costTier.length === 0 || (component.costTier && filters.costTier.includes(component.costTier));
      
      // Filter by visibility: only show 'Public' components or custom components (which are user's own)
      const visibilityMatch = component.visibility === 'Public' || component.isCustom;

      return searchMatch && typeMatch && complianceMatch && costMatch && visibilityMatch;
    });
  }, [searchTerm, filters, allComponents]);

  return (
    <div className="flex flex-col h-full">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-800">Component Marketplace</h1>
        <p className="text-neutral-600 mt-1">Discover, evaluate, and integrate AI components into your workflows.</p>
      </header>
      
      <div className="relative mb-6">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 text-neutral-400" />
        </div>
        <input
          type="text"
          placeholder="Search by name, description, or tags..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full pl-10 pr-3 py-3 border border-neutral-300 rounded-lg leading-5 bg-white text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm shadow-sm"
        />
      </div>

      <div className="flex flex-1 gap-6">
        <aside className="w-1/4 xl:w-1/5">
          <FilterPanel filters={filters} onFilterChange={handleFilterChange} />
        </aside>
        <main className="w-3/4 xl:w-4/5">
          {filteredComponents.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredComponents.map(component => (
                <ComponentCard key={component.id} component={component} onSelect={handleComponentSelect} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-10 text-center bg-white rounded-lg shadow">
              <SearchIcon className="w-16 h-16 text-neutral-300 mb-4" />
              <h3 className="text-xl font-semibold text-neutral-700">No Components Found</h3>
              <p className="text-neutral-500 mt-1">Try adjusting your search or filters.</p>
            </div>
          )}
        </main>
      </div>
      <ComponentDetailView component={selectedComponent} isOpen={!!selectedComponent} onClose={handleCloseDetailView} />
    </div>
  );
};

export default MarketplacePage;