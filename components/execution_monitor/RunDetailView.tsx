
import React from 'react';
import { WorkflowRun } from '../../types';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { PlayIcon } from '../../icons'; // Assuming appropriate icons

interface RunDetailViewProps {
  run: WorkflowRun | null;
  isOpen: boolean;
  onClose: () => void;
}

const DetailItem: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="grid grid-cols-3 gap-2 py-2 border-b border-neutral-100 last:border-b-0">
    <dt className="text-sm font-medium text-neutral-500">{label}</dt>
    <dd className="text-sm text-neutral-800 col-span-2">{value || '-'}</dd>
  </div>
);

const RunDetailView: React.FC<RunDetailViewProps> = ({ run, isOpen, onClose }) => {
  if (!run) return null;

  const formatDate = (dateString?: string) => {
    return dateString ? new Date(dateString).toLocaleString() : 'N/A';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Run Details: ${run.id.substring(0,8)}...`} size="lg">
      <dl className="divide-y divide-neutral-200">
        <DetailItem label="Run ID" value={run.id} />
        <DetailItem label="Workflow Name" value={run.workflowName} />
        <DetailItem label="Status" value={<span className={`font-semibold ${
            run.status === 'Success' ? 'text-status-success' :
            run.status === 'Failed' ? 'text-status-error' :
            run.status === 'Running' ? 'text-blue-600' : 'text-neutral-700'
          }`}>{run.status}</span>} />
        <DetailItem label="Start Time" value={formatDate(run.startTime)} />
        <DetailItem label="Duration" value={run.duration} />
        <DetailItem label="Cost" value={run.cost} />
        <DetailItem label="Initiator" value={run.initiator} />
      </dl>

      <div className="mt-6">
        <h4 className="text-md font-semibold text-neutral-700 mb-2">Logs & Metrics (Placeholder)</h4>
        <div className="p-4 bg-neutral-100 rounded-md text-sm text-neutral-500 min-h-[100px]">
          Real-time Gantt chart, logs, and resource metrics would be displayed here.
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-neutral-200 flex justify-end space-x-3">
        {run.status === 'Running' && <Button variant="danger" size="sm">Abort Run</Button>}
        <Button variant="secondary" size="sm" leftIcon={<PlayIcon className="w-4 h-4" />}>Rerun Workflow</Button>
        <Button variant="outline" onClick={onClose}>Close</Button>
      </div>
    </Modal>
  );
};

export default RunDetailView;