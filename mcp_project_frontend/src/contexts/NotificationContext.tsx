import React, { createContext, useState, useCallback } from 'react';

export interface Notification {
  id: string;
  user_id: string;
  message: string;
  type: string;
  read: boolean;
  timestamp: string;
}

interface NotificationContextType {
  notifications: Notification[];
  setNotifications: React.Dispatch<React.SetStateAction<Notification[]>>;
  markAsRead: (userId: string, notificationId: string) => void;
  fetchNotifications: (userId: string) => void;
}

export const NotificationContext = createContext<NotificationContextType>({
  notifications: [],
  setNotifications: () => {},
  markAsRead: () => {},
  fetchNotifications: () => {},
});

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const fetchNotifications = useCallback((userId: string) => {
    // TODO: Add real-time updates and notification preferences integration
    // TODO: Integrate with backend and real-time updates
    fetch(`/api/notifications?user_id=${userId}`)
      .then((res) => res.json())
      .then((data) => setNotifications(Array.isArray(data) ? data : []));
  }, []);

  const markAsRead = useCallback((userId: string, notificationId: string) => {
    fetch('/api/notifications/read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, notification_id: notificationId }),
    }).then(() => {
      setNotifications((prev) => prev.map(n => n.id === notificationId ? { ...n, read: true } : n));
    });
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, setNotifications, markAsRead, fetchNotifications }}>
      {children}
    </NotificationContext.Provider>
  );
}; 