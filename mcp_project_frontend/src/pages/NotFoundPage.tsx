import React from 'react';
import { useAnalytics } from '../hooks/useAnalytics';

const NotFoundPage: React.FC = () => {
  const { trackEvent } = useAnalytics();

  React.useEffect(() => {
    trackEvent('not_found_view');
  }, [trackEvent]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">404 - Page Not Found</h1>
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm p-6">
        <p className="text-neutral-600 dark:text-neutral-400">
          The page you are looking for does not exist.
        </p>
      </div>
    </div>
  );
};

export default NotFoundPage; 