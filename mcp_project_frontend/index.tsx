import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@context/AuthContext';
import { ComponentProvider } from '@context/ComponentContext'; // Import ComponentProvider

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ComponentProvider> {/* Wrap App with ComponentProvider */}
          <App />
        </ComponentProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);