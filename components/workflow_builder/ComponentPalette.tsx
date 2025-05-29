import React from 'react';
import Card from '../common/Card';
import { AIComponent } from '../../types';
import { CubeIcon, SearchIcon } from '../../icons';
import { useComponents } from '../../contexts/ComponentContext'; // Import useComponents

interface PaletteItemProps {
  component: AIComponent;
}

const PaletteItem: React.FC<PaletteItemProps> = ({ component }) => {
  const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: string, componentData: AIComponent) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/componentdata', JSON.stringify(componentData));
    event.dataTransfer.effectAllowed = 'move';
  };

  let itemIconDisplay: React.ReactNode;
  if (component.icon && React.isValidElement(component.icon)) {
    itemIconDisplay = React.cloneElement(component.icon as React.ReactElement<React.SVGProps<SVGSVGElement>>, { className: "w-5 h-5 text-primary flex-shrink-0" });
  } else {
    itemIconDisplay = <CubeIcon className="w-5 h-5 text-primary flex-shrink-0" />;
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

const ComponentPalette: React.FC = () => {
  const { allComponents } = useComponents(); // Use context
  const [searchTerm, setSearchTerm] = React.useState('');

  const availableForPalette = React.useMemo(() => {
    return allComponents.filter(c => 
      (c.visibility === 'Public' || c.isCustom) && // Show public components or user's own custom components
      (c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
       c.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
       (c.tags && c.tags.join(' ').toLowerCase().includes(searchTerm.toLowerCase())))
    );
  }, [allComponents, searchTerm]);

  const groupedComponents = availableForPalette.reduce((acc, component) => {
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
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-7 pr-2 py-1.5 text-xs border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-primary focus:border-primary"
          />
        </div>
      </div>
      <div className="p-3 space-y-4 overflow-y-auto flex-grow">
        {sortedGroupEntries.map(([type, components]) => (
          <div key={type}>
            <h4 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5">{type}</h4>
            <div className="space-y-1.5">
              {components.map(component => (
                <PaletteItem key={component.id} component={component} />
              ))}
            </div>
          </div>
        ))}
         {availableForPalette.length === 0 && (
          <p className="text-xs text-neutral-500 text-center py-4">No components match your search or filters.</p>
        )}
      </div>
    </Card>
  );
};

export default ComponentPalette;