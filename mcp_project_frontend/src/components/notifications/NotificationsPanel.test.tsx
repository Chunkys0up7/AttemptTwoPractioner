import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NotificationsPanel } from './NotificationsPanel';
import { NotificationProvider } from '../../contexts/NotificationContext';

const notifications = [
  { id: '1', user_id: 'demo', message: 'Test notification', type: 'info', read: false, timestamp: new Date().toISOString() },
  { id: '2', user_id: 'demo', message: 'Read notification', type: 'info', read: true, timestamp: new Date().toISOString() },
];

const server = setupServer(
  http.get('/api/notifications', () => HttpResponse.json(notifications)),
  http.post('/api/notifications/read', () => HttpResponse.json({ success: true }))
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const renderPanel = () => render(
  <NotificationProvider>
    <NotificationsPanel />
  </NotificationProvider>
);

test('shows loading and then notifications', async () => {
  renderPanel();
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  expect(await screen.findByText('Test notification')).toBeInTheDocument();
  expect(screen.getByText('Read notification')).toBeInTheDocument();
});

test('shows empty state if no notifications', async () => {
  server.use(http.get('/api/notifications', () => HttpResponse.json([])));
  renderPanel();
  expect(await screen.findByText(/no notifications/i)).toBeInTheDocument();
});

test('shows error on API failure', async () => {
  server.use(http.get('/api/notifications', () => new HttpResponse(null, { status: 500 })));
  renderPanel();
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});

// TODO: Add tests for mark as read, real-time updates, and preferences 