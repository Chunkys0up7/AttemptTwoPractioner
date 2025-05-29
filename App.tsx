import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Topbar from './components/layout/Topbar';
import DashboardPage from './pages/DashboardPage';
import MarketplacePage from './pages/MarketplacePage';
import WorkflowBuilderPage from './pages/WorkflowBuilderPage';
import ExecutionMonitorPage from './pages/ExecutionMonitorPage';
import SubmitComponentPage from './pages/SubmitComponentPage'; // Import new page
import { useAuth } from './hooks/useAuth';

// Mock LoginPage for demonstration
const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const handleLogin = () => {
    login({ id: 'user123', name: 'AI Ops User', email: 'user@example.com', avatarUrl: 'https://picsum.photos/seed/user123/100/100', role: 'Admin' });
  };
  return (
    <div className="flex items-center justify-center h-screen bg-neutral-100">
      <div className="p-8 bg-white shadow-xl rounded-lg text-center">
        <h1 className="text-2xl font-bold mb-6 text-primary">AI Ops Console</h1>
        <button 
          onClick={handleLogin}
          className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Login (Mock)
        </button>
      </div>
    </div>
  );
};


const AuthenticatedApp: React.FC = () => {
  return (
    <div className="flex h-screen bg-neutral-light overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64 overflow-hidden"> {/* Adjust ml to sidebar width */}
        <Topbar />
        <main className="flex-1 p-6 overflow-y-auto bg-neutral-100"> {/* Changed bg for content area distinction */}
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/marketplace" element={<MarketplacePage />} />
            <Route path="/marketplace/component/:componentId" element={<MarketplacePage />} /> {/* For detail view */}
            <Route path="/builder" element={<WorkflowBuilderPage />} />
            <Route path="/builder/:workflowId" element={<WorkflowBuilderPage />} />
            <Route path="/monitor" element={<ExecutionMonitorPage />} />
            <Route path="/monitor/run/:runId" element={<ExecutionMonitorPage />} /> {/* For detail view */}
            <Route path="/submit-component" element={<SubmitComponentPage />} /> {/* New route */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} /> {/* Fallback */}
          </Routes>
        </main>
      </div>
    </div>
  );
}


const App: React.FC = () => {
  const { user } = useAuth();

  return (
    <HashRouter>
      <Routes>
        {!user && <Route path="/login" element={<LoginPage />} />}
        {!user && <Route path="/*" element={<Navigate to="/login" replace />} />}
        {user && <Route path="/*" element={<AuthenticatedApp />} />}
      </Routes>
    </HashRouter>
  );
};

export default App;