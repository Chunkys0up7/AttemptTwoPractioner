import React from 'react';

interface IconProps {
  className?: string;
}

const EndIcon: React.FC<IconProps> = ({ className = "w-8 h-8 text-gray-400" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default EndIcon;
