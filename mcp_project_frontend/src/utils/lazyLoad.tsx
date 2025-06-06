import React, { Suspense, useEffect, useState } from 'react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import PerformanceService from '../services/performanceService';

interface LazyLoadOptions {
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  trackLoading?: boolean;
  preload?: boolean;
  retryCount?: number;
  retryDelay?: number;
}

interface LoadingProgress {
  progress: number;
  status: 'loading' | 'error' | 'success';
}

export function lazyLoad<T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  options: LazyLoadOptions = {}
) {
  const {
    fallback = <LoadingSpinner />,
    errorFallback = <ErrorMessage message="Failed to load component" />,
    trackLoading = true,
    preload = false,
    retryCount = 3,
    retryDelay = 1000,
  } = options;

  const LazyComponent = React.lazy(importFn);
  const performanceService = PerformanceService.getInstance();

  // Preload the component if specified
  if (preload) {
    importFn().catch(console.error);
  }

  return function LazyLoadedComponent(props: React.ComponentProps<T>) {
    const [loadingState, setLoadingState] = useState<LoadingProgress>({
      progress: 0,
      status: 'loading',
    });
    const [retryAttempt, setRetryAttempt] = useState(0);
    const startTime = trackLoading ? performance.now() : 0;

    useEffect(() => {
      if (trackLoading) {
        const loadTime = performance.now() - startTime;
        performanceService.recordMetric('component_load', loadTime);
      }
    }, [trackLoading, startTime]);

    const handleRetry = () => {
      if (retryAttempt < retryCount) {
        setRetryAttempt(prev => prev + 1);
        setLoadingState({ progress: 0, status: 'loading' });
      }
    };

    const LoadingProgressIndicator = () => (
      <div className="flex flex-col items-center justify-center p-4">
        <LoadingSpinner />
        <div className="mt-2 text-sm text-gray-600">
          Loading... {Math.round(loadingState.progress)}%
        </div>
      </div>
    );

    return (
      <Suspense fallback={<LoadingProgressIndicator />}>
        <ErrorBoundary 
          fallback={
            <div className="flex flex-col items-center justify-center p-4">
              {errorFallback}
              {retryAttempt < retryCount && (
                <button
                  onClick={handleRetry}
                  className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Retry Loading
                </button>
              )}
            </div>
          }
          onError={(error) => {
            console.error('Error in lazy loaded component:', error);
            setLoadingState({ progress: 0, status: 'error' });
          }}
        >
          <LazyComponent {...props} />
        </ErrorBoundary>
      </Suspense>
    );
  };
}

class ErrorBoundary extends React.Component<
  { 
    children: React.ReactNode; 
    fallback: React.ReactNode;
    onError?: (error: Error) => void;
  },
  { hasError: boolean }
> {
  constructor(props: { 
    children: React.ReactNode; 
    fallback: React.ReactNode;
    onError?: (error: Error) => void;
  }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
} 