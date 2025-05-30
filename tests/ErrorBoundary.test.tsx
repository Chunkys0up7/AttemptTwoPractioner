import React from 'react';
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../src/components/common/ErrorBoundary';

function ProblemChild() {
  throw new Error('Test error!');
  return null;
}

describe('ErrorBoundary', () => {
  it('renders fallback UI when a child throws', () => {
    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/test error/i)).toBeInTheDocument();
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Safe Child</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Safe Child')).toBeInTheDocument();
  });
});
