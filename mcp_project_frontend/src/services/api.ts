import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';  // FastAPI default port

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  preferences: {
    get: () => api.get('/preferences/me'),
    create: (data: any) => api.post('/preferences/me', data),
    update: (data: any) => api.put('/preferences/me', data),
    delete: () => api.delete('/preferences/me'),
  },
  sync: {
    get: () => api.get('/sync'),
    create: (data: any) => api.post('/sync', data),
    update: (id: string, data: any) => api.put(`/sync/${id}`, data),
    delete: (id: string) => api.delete(`/sync/${id}`),
  },
  analytics: {
    get: () => api.get('/analytics'),
    create: (data: any) => api.post('/analytics', data),
    update: (id: string, data: any) => api.put(`/analytics/${id}`, data),
    delete: (id: string) => api.delete(`/analytics/${id}`),
  },
}; 