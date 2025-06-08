import React, { createContext } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WebSocketContextType {
  connected: boolean;
  lastMessage: any;
  error: string | null;
}

export const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  lastMessage: null,
  error: null,
});

export const WebSocketProvider: React.FC<{ userId: string; children: React.ReactNode }> = ({ userId, children }) => {
  const { connected, lastMessage, error } = useWebSocket(userId);
  // TODO: Add advanced features (reconnect, error handling, message queue)
  return (
    <WebSocketContext.Provider value={{ connected, lastMessage, error }}>
      {children}
    </WebSocketContext.Provider>
  );
}; 