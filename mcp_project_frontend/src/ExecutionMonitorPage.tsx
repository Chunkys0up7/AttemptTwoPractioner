
import React, { useState, useEffect } from 'react';
import { DUMMY_WORKFLOW_RUNS } from '../constants';
import RunsTable from '../components/execution_monitor/RunsTable';
import RunDetailView from '../components/execution_monitor/RunDetailView';
import { WorkflowRun, WorkflowRunStatus } from '../types';
import { FilterIcon } from '../icons';
import { useParams, useNavigate } from 'react-router-dom';

const ExecutionMonitorPage: React.FC = () => {
  const [runs, setRuns] = useState<WorkflowRun[]>(DUMMY_WORKFLOW_RUNS);
  const [selectedRun, setSelectedRun] = useState<WorkflowRun | null>(null);
  const [statusFilter, setStatusFilter] = useState<WorkflowRunStatus | 'All'>('All');

  const { runId } = useParams<{ runId?: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (runId) {
      const run = DUMMY_WORKFLOW_RUNS.find(r => r.id === runId);
      if (run) {
        setSelectedRun(run);
      } else {
        navigate('/monitor', { replace: true });
      }
    } else {
      setSelectedRun(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  const handleSelectRun = (run: WorkflowRun) => {
    setSelectedRun(run);
    navigate(`/monitor/run/${run.id}`);
  };

  const handleCloseDetailView = () => {
    setSelectedRun(null);
    navigate('/monitor');
  };

  const filteredRuns = statusFilter === 'All' 
    ? runs 
    : runs.filter(run => run.status === statusFilter);

  return (
    <div className="flex flex-col h-full">
      <header className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-neutral-800">Execution Monitor</h1>
          <p className="text-neutral-600 mt-1">Track live and historical workflow runs, manage resources, and debug.</p>
        </div>
        <div className="flex items-center space-x-2">
          <FilterIcon className="w-5 h-5 text-neutral-500"/>
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value as WorkflowRunStatus | 'All')}
            className="px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900 focus:ring-primary focus:border-primary shadow-sm"
          >
            <option value="All">All Statuses</option>
            {Object.values(WorkflowRunStatus).map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
        </div>
      </header>
      
      <RunsTable runs={filteredRuns} onSelectRun={handleSelectRun} />
      
      <RunDetailView run={selectedRun} isOpen={!!selectedRun} onClose={handleCloseDetailView} />
    </div>
  );
};

export default ExecutionMonitorPage;