import React from 'react';
import Card from '../common/Card';
import {
  ALL_COMPONENT_TYPES,
  COMPONENT_COMPLIANCE_OPTIONS,
  COMPONENT_COST_TIERS,
} from '../../constants';
import { FilterIcon } from '../../icons';

interface FilterPanelProps {
  filters: Record<string, any>;
  onFilterChange: (filterName: string, value: any) => void;
}

const FilterGroup: React.FC<{ title: string; children: React.ReactNode }> = ({
  title,
  children,
}) => (
  <div className="border-b border-neutral-200 last:border-b-0 pb-6 last:pb-0">
    <h4 className="text-sm font-semibold text-neutral-700 mb-3">{title}</h4>
    <div className="space-y-2">{children}</div>
  </div>
);

const CheckboxFilter: React.FC<{
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}> = ({ label, checked, onChange }) => (
  <label className="flex items-center space-x-2 text-sm text-neutral-600 hover:text-primary cursor-pointer group">
    <input
      type="checkbox"
      checked={checked}
      onChange={e => onChange(e.target.checked)}
      className="form-checkbox h-4 w-4 text-primary border-neutral-300 rounded focus:ring-primary transition-colors duration-150 ease-in-out group-hover:border-primary"
    />
    <span className="group-hover:text-primary transition-colors duration-150 ease-in-out">
      {label}
    </span>
  </label>
);

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange }) => {
  const handleCheckboxGroupChange = (filterName: string, option: string, isChecked: boolean) => {
    const currentValues = Array.isArray(filters[filterName]) ? filters[filterName] : [];
    const newValues = isChecked
      ? [...currentValues, option]
      : currentValues.filter((v: string) => v !== option);
    onFilterChange(filterName, newValues);
  };

  return (
    <Card
      title="Filters"
      className="sticky top-20"
      titleClassName="text-base font-semibold text-neutral-800"
      actions={<FilterIcon className="w-5 h-5 text-primary" />}
    >
      <div className="space-y-6">
        <FilterGroup title="Component Type">
          {ALL_COMPONENT_TYPES.map(type => (
            <CheckboxFilter
              key={type}
              label={type}
              checked={(filters.type || []).includes(type)}
              onChange={isChecked => handleCheckboxGroupChange('type', type, isChecked)}
            />
          ))}
        </FilterGroup>

        <FilterGroup title="Compliance">
          {COMPONENT_COMPLIANCE_OPTIONS.map(compliance => (
            <CheckboxFilter
              key={compliance}
              label={compliance}
              checked={(filters.compliance || []).includes(compliance)}
              onChange={isChecked => handleCheckboxGroupChange('compliance', compliance, isChecked)}
            />
          ))}
        </FilterGroup>

        <FilterGroup title="Cost Tier">
          {COMPONENT_COST_TIERS.map(cost => (
            <CheckboxFilter
              key={cost}
              label={cost}
              checked={(filters.costTier || []).includes(cost)}
              onChange={isChecked => handleCheckboxGroupChange('costTier', cost, isChecked)}
            />
          ))}
        </FilterGroup>
      </div>
    </Card>
  );
};

export default FilterPanel;
