import React from 'react';

interface IconProps {
  className?: string;
}

const DataIcon: React.FC<IconProps> = ({ className = "w-8 h-8 text-gray-400" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

export default DataIcon;
