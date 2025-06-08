import React, { createContext } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WebSocketContextType {
  connected: boolean;
  lastMessage: any;
}

export const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  lastMessage: null,
});

export const WebSocketProvider: React.FC<{ userId: string; children: React.ReactNode }> = ({ userId, children }) => {
  const { connected, lastMessage } = useWebSocket(userId);
  // TODO: Add advanced features (reconnect, error handling, message queue)
  return (
    <WebSocketContext.Provider value={{ connected, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
}; 