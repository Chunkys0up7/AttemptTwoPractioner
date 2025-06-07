import React from 'react';
import Card from '@components/common/Card';
import { AIComponent } from '../types/index';
import type { SpecificComponentType } from '../types/index';
import { SearchIcon } from '@components/icons/ui';
import DefaultIcon from '@components/icons/DefaultIcon';
import { useComponents } from '@context/index';
import type { ComponentPaletteProps, PaletteItemProps } from './types';

const ComponentPalette: React.FC<ComponentPaletteProps> = () => {
  const {
    components,
    loading,
    error,
    isFetching,
    isCached,
    fetchComponents,
    filterComponents,
    sortComponents
  } = useComponents();

  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedTypes, setSelectedTypes] = React.useState<string[]>([]);
  const [sortField, setSortField] = React.useState<keyof AIComponent>('name');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('asc');

  const availableForPalette = React.useMemo(() => {
    if (!components) return [];
    const filtered = filterComponents(searchTerm, selectedTypes as SpecificComponentType[]);
    return filtered.filter((component) => 
      component.visibility === 'public' || component.isCustom
    );
  }, [components, searchTerm, selectedTypes, filterComponents]);

  React.useEffect(() => {
    if (!components?.length && !loading && !isFetching) {
      fetchComponents();
    }
  }, [components, loading, isFetching, fetchComponents]);

  const handleSort = (field: keyof AIComponent) => {
    setSortField(field);
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    sortComponents(field, prev => prev === 'asc' ? 'desc' : 'asc');
  };

  if (error) {
    return (
      <div className="p-4">
        <div className="text-red-500 mb-2">Error: {error}</div>
        <button
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          onClick={() => fetchComponents()}
        >
          Retry
        </button>
      </div>
    );
  }

  if (loading || isFetching) {
    return (
      <div className="flex flex-col items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mb-2"></div>
        <p className="text-sm text-neutral-500">
          {isFetching ? 'Refreshing components...' : 'Loading components...'}
        </p>
      </div>
    );
  }

  if (!components?.length) {
    return (
      <div className="p-4 text-center">
        <p className="text-neutral-500 mb-2">No components available</p>
        <button
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          onClick={() => fetchComponents()}
        >
          Refresh
        </button>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  if (loading) {
    return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>;
  }

  const groupedComponents = availableForPalette.reduce((acc: Record<string, AIComponent[]>, component) => {
    const typeKey = component.isCustom ? 'My Custom Components' : component.type;
    if (!acc[typeKey]) {
      acc[typeKey] = [];
    }
    acc[typeKey].push(component);
    return acc;
  }, {} as Record<string, AIComponent[]>);

  // Ensure 'My Custom Components' appears first if it exists
  const sortedGroupEntries = Object.entries(groupedComponents).sort(([keyA], [keyB]) => {
    if (keyA === 'My Custom Components') return -1;
    if (keyB === 'My Custom Components') return 1;
    return keyA.localeCompare(keyB);
  });

  const PaletteItem: React.FC<PaletteItemProps> = ({ component }: PaletteItemProps) => {
    const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: string, componentData: AIComponent) => {
      event.dataTransfer.setData('application/reactflow', nodeType);
      event.dataTransfer.setData('application/componentdata', JSON.stringify(componentData));
      event.dataTransfer.effectAllowed = 'move';
    };

    // Get appropriate icon based on component type
    let itemIconDisplay: React.ReactNode;
    switch (component.type) {
      case SpecificComponentType.LLM_PROMPT_AGENT:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      case SpecificComponentType.PYTHON_SCRIPT:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      case SpecificComponentType.JUPYTER_NOTEBOOK:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      case SpecificComponentType.DATA_PROCESSOR:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      case SpecificComponentType.MODEL_TRAINER:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      case SpecificComponentType.CUSTOM:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
        break;
      default:
        itemIconDisplay = <DefaultIcon className="w-5 h-5 text-primary flex-shrink-0" />;
    }

    return (
      <div
        className="p-2.5 border border-neutral-200 bg-white rounded-md shadow-sm hover:shadow-md cursor-grab active:cursor-grabbing transition-all flex items-center space-x-2"
        draggable
        onDragStart={(event) => onDragStart(event, 'customComponentNode', component)}
      >
        {itemIconDisplay}
        <span className="text-xs font-medium text-neutral-700 truncate" title={component.name}>{component.name}</span>
      </div>
    );
  };

  return (
    <Card title="Component Palette" className="h-full flex flex-col" noPadding>
      <div className="p-3 border-b border-neutral-200">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
            <SearchIcon className="h-4 w-4 text-neutral-400" />
          </div>
          <input
            type="text"
            placeholder="Search components..."
            value=""
            className="block w-full pl-7 pr-2 py-1.5 text-xs border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-primary focus:border-primary"
          />
        </div>
      </div>
      <div className="p-3 space-y-4 overflow-y-auto flex-grow">
        {error && (
          <p className="text-xs text-red-500 text-center py-4">{error}</p>
        )}
        {loading && (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
          </div>
        )}
        {!loading && sortedGroupEntries.map(([type, components]) => (
          <div key={type}>
            <h4 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5">{type}</h4>
            <div className="space-y-1.5">
              {components.map((component) => (
                <PaletteItem key={component.id} component={component} />
              ))}
            </div>
          </div>
        ))}
        {!loading && availableForPalette.length === 0 && (
          <p className="text-xs text-neutral-500 text-center py-4">No components match your search or filters.</p>
        )}
      </div>
    </Card>
  );
};

export default ComponentPalette;