import React, { ReactNode } from 'react';
import { XCircleIcon } from '../../icons';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  footer?: ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, size = 'md', footer }) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full h-full rounded-none',
  };

  // Keyboard handler for accessibility
  const handleBackdropKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onClose();
    }
  };

  return (
    // eslint-disable-next-line jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events
    <div
      className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 dark:bg-neutral-900/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 transition-opacity duration-300 ease-in-out"
      onClick={onClose}
      role="button"
      tabIndex={0}
      aria-label="Close modal"
      onKeyDown={handleBackdropKeyDown}
    >
      <div
        className={`bg-white dark:bg-neutral-900 rounded-lg shadow-xl transform transition-all duration-300 ease-in-out w-full ${sizeClasses[size]} flex flex-col max-h-[90vh] border border-neutral-200 dark:border-neutral-700`}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
          {title && <h2 className="text-xl font-semibold text-neutral-800 dark:text-neutral-100">{title}</h2>}
          <button onClick={onClose} className="text-neutral-400 hover:text-neutral-600 dark:text-neutral-500 dark:hover:text-neutral-300">
            <XCircleIcon className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto flex-grow text-neutral-800 dark:text-neutral-100">
          {children}
        </div>
        {footer && (
          <div className="p-4 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 rounded-b-lg">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;