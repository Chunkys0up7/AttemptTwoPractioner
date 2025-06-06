import React, { useEffect, useState } from 'react';
import PerformanceService from '../../services/performanceService';
import { PerformanceReport } from '../../types/performance';

const PerformanceDashboard: React.FC = () => {
  const [report, setReport] = useState<PerformanceReport | null>(null);
  const performanceService = PerformanceService.getInstance();

  useEffect(() => {
    const updateReport = () => {
      setReport(performanceService.getReport());
    };

    // Update report every 5 seconds
    const interval = setInterval(updateReport, 5000);
    updateReport(); // Initial update

    return () => clearInterval(interval);
  }, []);

  if (!report) return null;

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(report.summary).map(([type, summary]) => (
          <div key={type} className="p-4 bg-gray-50 rounded">
            <h3 className="font-medium text-gray-700 mb-2">{type.toUpperCase()}</h3>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Latest:</span>
                <span className="font-mono">{summary.latest.toFixed(2)}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Average:</span>
                <span className="font-mono">{summary.average.toFixed(2)}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Min:</span>
                <span className="font-mono">{summary.min.toFixed(2)}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Max:</span>
                <span className="font-mono">{summary.max.toFixed(2)}ms</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PerformanceDashboard; 