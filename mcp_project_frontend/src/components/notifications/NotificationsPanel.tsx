import React, { useEffect, useContext } from 'react';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';
import { EmptyState } from '../common/EmptyState';
import { NotificationContext, Notification } from '../../contexts/NotificationContext';

export const NotificationsPanel: React.FC = () => {
  // TODO: Replace with real user context
  const userId = 'demo';
  const { notifications, setNotifications, markAsRead, fetchNotifications } = useContext(NotificationContext);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/notifications?user_id=${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch notifications');
        return res.json();
      })
      .then((data) => setNotifications(Array.isArray(data) ? data : []))
      .catch((err) => setError(err.message || 'Failed to load notifications'))
      .finally(() => setLoading(false));
    // TODO: Use fetchNotifications from context instead of direct fetch
    // fetchNotifications(userId);
  }, [userId, setNotifications]);

  const handleMarkAsRead = (id: string) => {
    markAsRead(userId, id);
    // setNotifications will be updated by context
  };

  if (loading) return <LoadingSpinner size="md" color="primary" className="mx-auto" />;
  if (error) return <ErrorMessage message={error} />;
  if (notifications.length === 0) return <EmptyState message="No notifications." />;

  return (
    <section aria-label="Notifications">
      <h3>Notifications</h3>
      <ul>
        {notifications.map((notif) => (
          <li key={notif.id} style={{ opacity: notif.read ? 0.6 : 1 }}>
            <span>{notif.message}</span>
            {!notif.read && (
              <button onClick={() => handleMarkAsRead(notif.id)} aria-label="Mark as read">Mark as read</button>
            )}
            <span className="timestamp">{new Date(notif.timestamp).toLocaleString()}</span>
          </li>
        ))}
      </ul>
      {/* TODO: Add real-time updates and notification preferences */}
    </section>
  );
}; 