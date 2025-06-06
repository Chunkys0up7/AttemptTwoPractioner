import React from 'react';

interface IconProps {
  className?: string;
}

const ActionIcon: React.FC<IconProps> = ({ className = "w-8 h-8 text-gray-400" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

export default ActionIcon;
