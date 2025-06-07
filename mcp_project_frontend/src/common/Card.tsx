
import React, { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  titleClassName?: string;
  actions?: ReactNode;
  onClick?: () => void;
  noPadding?: boolean;
}

const Card: React.FC<CardProps> = ({ children, className = '', title, titleClassName = '', actions, onClick, noPadding = false }) => {
  const baseClasses = "bg-white shadow-lg rounded-xl overflow-hidden transition-all duration-300 ease-in-out";
  const clickableClasses = onClick ? "hover:shadow-xl cursor-pointer" : "";
  
  return (
    <div className={`${baseClasses} ${clickableClasses} ${className}`} onClick={onClick}>
      {(title || actions) && (
        <div className={`flex justify-between items-center ${noPadding ? 'px-0 py-0' : 'px-5 py-4'} border-b border-neutral-200`}>
          {title && <h3 className={`text-lg font-semibold text-neutral-800 ${titleClassName}`}>{title}</h3>}
          {actions && <div className="flex items-center space-x-2">{actions}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-5'}>
        {children}
      </div>
    </div>
  );
};

export { Card };