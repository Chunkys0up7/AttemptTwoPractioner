import { endpoints } from './api';
import { PerformanceMetric, PerformanceReport, PerformanceSummary } from '../types/performance';

interface PerformanceEvent {
  type: string;
  timestamp: number;
  duration?: number;
}

class PerformanceService {
  private static instance: PerformanceService;
  private metrics: Map<string, PerformanceMetric[]>;
  private events: PerformanceEvent[];
  private readonly MAX_METRICS_PER_TYPE = 100;
  private readonly MAX_BUFFER_SIZE = 100;
  private readonly FLUSH_INTERVAL = 60000; // 1 minute

  private constructor() {
    this.metrics = new Map();
    this.events = [];
    this.initializePerformanceObserver();
    // Start periodic flushing
    setInterval(() => this.flush(), this.FLUSH_INTERVAL);
    
    // Track page load performance
    this.trackPageLoad();
    
    // Track navigation performance
    this.trackNavigation();
  }

  public static getInstance(): PerformanceService {
    if (!PerformanceService.instance) {
      PerformanceService.instance = new PerformanceService();
    }
    return PerformanceService.instance;
  }

  private initializePerformanceObserver(): void {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      // Observe Largest Contentful Paint
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          this.recordMetric('lcp', entry.startTime);
        });
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // Observe First Input Delay
      const fidObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          if ('processingStart' in entry && typeof entry.processingStart === 'number') {
            this.recordMetric('fid', entry.processingStart - entry.startTime);
          }
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // Observe Cumulative Layout Shift
      const clsObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          if ('value' in entry && typeof entry.value === 'number') {
            this.recordMetric('cls', entry.value);
          }
        });
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    }
  }

  public recordMetric(type: string, value: number): void {
    const metrics = this.metrics.get(type) || [];
    const newMetrics = [...metrics, { timestamp: Date.now(), value }];
    
    // Keep only the most recent metrics
    if (newMetrics.length > this.MAX_METRICS_PER_TYPE) {
      newMetrics.shift();
    }

    this.metrics.set(type, newMetrics);
  }

  public getMetrics(type?: string): PerformanceMetric[] {
    if (type) {
      return this.metrics.get(type) || [];
    }
    return Array.from(this.metrics.values()).flat();
  }

  public getReport(): PerformanceReport {
    const report: PerformanceReport = {
      timestamp: Date.now(),
      metrics: {},
      summary: {},
    };

    this.metrics.forEach((metrics, type) => {
      if (metrics.length > 0) {
        const values = metrics.map(m => m.value);
        report.metrics[type] = metrics;
        report.summary[type] = {
          average: values.reduce((a, b) => a + b, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values),
          latest: values[values.length - 1],
        };
      }
    });

    return report;
  }

  public clearMetrics(): void {
    this.metrics.clear();
  }

  private trackPageLoad() {
    if (typeof window !== 'undefined') {
      window.addEventListener('load', () => {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        this.recordMetric('page_load', loadTime);
      });
    }
  }

  private trackNavigation() {
    if (typeof window !== 'undefined') {
      window.addEventListener('popstate', () => {
        this.recordMetric('navigation', performance.now());
      });
    }
  }

  private flush() {
    const report = this.getReport();
    // Here you would typically send the report to your analytics backend
    console.log('Performance Report:', report);
    this.clearMetrics();
  }

  public trackApiCall(endpoint: string, duration: number, status: number) {
    this.recordMetric('api_call', duration);
  }

  public trackComponentRender(componentName: string, duration: number) {
    this.recordMetric('component_render', duration);
  }
}

export default PerformanceService; 