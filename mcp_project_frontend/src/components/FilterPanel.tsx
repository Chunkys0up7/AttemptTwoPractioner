import React from 'react';

interface FilterPanelProps {
  selectedTags: string[];
  onTagSelect: (tags: string[]) => void;
  availableTags: string[];
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  selectedTags,
  onTagSelect,
  availableTags
}) => {
  const handleTagToggle = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];
    onTagSelect(newTags);
  };

  return (
    <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm p-4">
      <h3 className="text-lg font-semibold text-neutral-800 dark:text-neutral-100 mb-4">
        Filter by Tags
      </h3>
      <div className="space-y-2">
        {availableTags.map(tag => (
          <label key={tag} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedTags.includes(tag)}
              onChange={() => handleTagToggle(tag)}
              className="rounded border-neutral-300 text-primary focus:ring-primary"
            />
            <span className="text-sm text-neutral-700 dark:text-neutral-300">{tag}</span>
          </label>
        ))}
      </div>
    </div>
  );
}; 