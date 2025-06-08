import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { RecommendationsPanel } from './RecommendationsPanel';

const recommendations = [
  { id: 1, title: 'Rec 1', category: 'A', score: 0.9 },
  { id: 2, title: 'Rec 2', category: 'B', score: 0.8 },
  { id: 3, title: 'Rec 3', category: 'A', score: 0.7 },
];

const server = setupServer(
  http.get('/api/recommendations', ({ request }) => {
    const url = new URL(request.url);
    const category = url.searchParams.get('category');
    const top_n = url.searchParams.get('top_n');
    let filtered = recommendations;
    if (category) filtered = filtered.filter(r => r.category === category);
    if (top_n) filtered = filtered.slice(0, Number(top_n));
    return HttpResponse.json(filtered);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('shows loading and then recommendations', async () => {
  render(<RecommendationsPanel />);
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  expect(await screen.findByText('Rec 1')).toBeInTheDocument();
  expect(screen.getByText('Rec 2')).toBeInTheDocument();
});

test('filters by category', async () => {
  render(<RecommendationsPanel />);
  // Simulate category filter UI if present, or call with prop/context if needed
  // For this test, we assume a filter UI exists
  const categoryInput = screen.getByLabelText(/category/i);
  userEvent.clear(categoryInput);
  userEvent.type(categoryInput, 'A');
  userEvent.tab();
  await waitFor(() => expect(screen.getByText('Rec 1')).toBeInTheDocument());
  expect(screen.getByText('Rec 3')).toBeInTheDocument();
  expect(screen.queryByText('Rec 2')).not.toBeInTheDocument();
});

test('limits to top_n', async () => {
  render(<RecommendationsPanel />);
  const topNInput = screen.getByLabelText(/top n/i);
  userEvent.clear(topNInput);
  userEvent.type(topNInput, '1');
  userEvent.tab();
  await waitFor(() => expect(screen.getByText('Rec 1')).toBeInTheDocument());
  expect(screen.queryByText('Rec 2')).not.toBeInTheDocument();
});

test('shows error on API failure', async () => {
  server.use(
    http.get('/api/recommendations', () => new HttpResponse(null, { status: 500 }))
  );
  render(<RecommendationsPanel />);
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});

test('shows empty state if no recommendations', async () => {
  server.use(
    http.get('/api/recommendations', () => HttpResponse.json([]))
  );
  render(<RecommendationsPanel />);
  expect(await screen.findByText(/no recommendations/i)).toBeInTheDocument();
}); 