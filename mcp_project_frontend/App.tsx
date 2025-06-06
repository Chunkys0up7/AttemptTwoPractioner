import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '@layout/Sidebar';
import Topbar from '@layout/Topbar';
import DashboardPage from '@pages/DashboardPage';
import MarketplacePage from '@pages/MarketplacePage';
import WorkflowBuilderPage from '@pages/WorkflowBuilderPage';
import ExecutionMonitorPage from '@pages/ExecutionMonitorPage';
import SubmitComponentPage from '@pages/SubmitComponentPage';
import { AuthProvider } from "@context/AuthContext";
import LoginPage from '@pages/LoginPage';

const AuthenticatedApp = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/marketplace" element={<MarketplacePage />} />
            <Route path="/builder" element={<WorkflowBuilderPage />} />
            <Route path="/monitor" element={<ExecutionMonitorPage />} />
            <Route path="/submit-component" element={<SubmitComponentPage />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<AuthenticatedApp />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
