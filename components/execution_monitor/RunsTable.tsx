
import React from 'react';
import { WorkflowRun, WorkflowRunStatus } from '../../types';
import { CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon, PlayIcon, XCircleIcon } from '../../icons';
import Button from '../common/Button';
import { EyeIcon } from '../../icons';

interface RunsTableProps {
  runs: WorkflowRun[];
  onSelectRun: (run: WorkflowRun) => void;
}

const StatusBadge: React.FC<{ status: WorkflowRunStatus }> = ({ status }) => {
  let bgColor, textColor, Icon;
  switch (status) {
    case WorkflowRunStatus.Success:
      bgColor = 'bg-green-100'; textColor = 'text-green-700'; Icon = CheckCircleIcon; break;
    case WorkflowRunStatus.Running:
      bgColor = 'bg-blue-100'; textColor = 'text-blue-700'; Icon = PlayIcon; break; // Using Play for Running
    case WorkflowRunStatus.Failed:
      bgColor = 'bg-red-100'; textColor = 'text-red-700'; Icon = XCircleIcon; break;
    case WorkflowRunStatus.Pending:
      bgColor = 'bg-yellow-100'; textColor = 'text-yellow-700'; Icon = InformationCircleIcon; break;
    case WorkflowRunStatus.Aborted:
      bgColor = 'bg-neutral-200'; textColor = 'text-neutral-600'; Icon = ExclamationTriangleIcon; break;
    default:
      bgColor = 'bg-neutral-100'; textColor = 'text-neutral-500'; Icon = InformationCircleIcon;
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
      <Icon className="w-3 h-3 mr-1.5" />
      {status}
    </span>
  );
};

const RunsTable: React.FC<RunsTableProps> = ({ runs, onSelectRun }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white shadow-lg rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Run ID</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Workflow Name</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Status</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Start Time</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Duration</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Cost</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Initiator</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200">
            {runs.map((run) => (
              <tr key={run.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-800 truncate" title={run.id}>{run.id.substring(0,8)}...</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">{run.workflowName}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <StatusBadge status={run.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">{formatDate(run.startTime)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">{run.duration || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">{run.cost || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">{run.initiator || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <Button variant="ghost" size="sm" onClick={() => onSelectRun(run)} leftIcon={<EyeIcon className="w-4 h-4"/>}>
                    Details
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {runs.length === 0 && (
        <div className="text-center py-10 text-neutral-500">
          <InformationCircleIcon className="w-12 h-12 mx-auto mb-2 text-neutral-300" />
          No workflow runs found.
        </div>
      )}
    </div>
  );
};

export default RunsTable;