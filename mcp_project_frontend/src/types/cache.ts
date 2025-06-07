import { Node, Edge } from '../workflow';

export interface CacheEntry {
  nodes: Record<string, Node>;
  edges: Record<string, Edge>;
  metadata: Record<string, any>;
  timestamp: number;
  size: number;
}

export interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  averageTTL: number;
  maxEntrySize: number;
  minEntrySize: number;
}

export interface CacheConfig {
  timeout?: number;
  maxSize?: number;
  cleanupInterval?: number;
  maxSizeMB?: number;
}

export interface CacheEvent {
  type: 'store' | 'retrieve' | 'cleanup' | 'clear';
  data?: {
    key?: string;
    entriesRemoved?: number;
    totalEntries?: number;
    size?: number;
  };
}

export interface CacheOptions {
  validate?: boolean;
  compress?: boolean;
  encrypt?: boolean;
}
