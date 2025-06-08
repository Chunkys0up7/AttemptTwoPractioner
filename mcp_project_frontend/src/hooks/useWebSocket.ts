import { useEffect, useRef, useState, useCallback } from 'react';

export function useWebSocket(userId: string) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!userId) return;
    setError(null);
    const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/notifications?user_id=${userId}`);
    wsRef.current = ws;
    ws.onopen = () => {
      setConnected(true);
      setError(null);
      reconnectAttempts.current = 0;
    };
    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect with exponential backoff
      if (reconnectAttempts.current < 5) {
        const timeout = Math.min(1000 * 2 ** reconnectAttempts.current, 10000);
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, timeout);
      } else {
        setError('Unable to connect to real-time updates.');
      }
    };
    ws.onerror = (e) => {
      setConnected(false);
      setError('WebSocket error occurred.');
      ws.close();
    };
    ws.onmessage = (event) => {
      try {
        setLastMessage(JSON.parse(event.data));
      } catch {
        setLastMessage(event.data);
      }
    };
  }, [userId]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);

  // TODO: Add authentication and advanced error reporting

  return { connected, lastMessage, error };
} 