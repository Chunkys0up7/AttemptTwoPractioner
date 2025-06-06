export interface PerformanceMetric {
  timestamp: number;
  value: number;
}

export interface PerformanceSummary {
  average: number;
  min: number;
  max: number;
  latest: number;
}

export interface PerformanceReport {
  timestamp: number;
  metrics: Record<string, PerformanceMetric[]>;
  summary: Record<string, PerformanceSummary>;
} 