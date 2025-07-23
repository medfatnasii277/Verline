import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { webSocketService, NotificationData, UnreadCountData } from '../services/websocket';
import { api } from '../services/api';

interface NotificationsContextType {
  notifications: NotificationData[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (notificationId: number) => void;
  markAllAsRead: () => void;
  refreshNotifications: () => void;
}

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

interface NotificationsProviderProps {
  children: ReactNode;
}

export const NotificationsProvider: React.FC<NotificationsProviderProps> = ({ children }) => {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket connection when user is authenticated
  useEffect(() => {
    if (user && token) {
      console.log('Connecting WebSocket for user:', user.id);
      webSocketService.connect(user.id, token);

      // Set up event listeners
      const handleConnect = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      const handleDisconnect = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };

      const handleNotification = (data: NotificationData) => {
        console.log('New notification received:', data);
        setNotifications(prev => [data, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // Show browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification(data.message, {
            icon: '/favicon.ico',
            badge: '/favicon.ico'
          });
        }
      };

      const handleUnreadCount = (data: UnreadCountData) => {
        console.log('Unread count updated:', data.count);
        setUnreadCount(data.count);
      };

      const handleNotificationsList = (data: NotificationData[]) => {
        console.log('Notifications list received:', data);
        setNotifications(data);
      };

      const handleError = (error: any) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      // Register event listeners
      webSocketService.on('connect', handleConnect);
      webSocketService.on('disconnect', handleDisconnect);
      webSocketService.on('notification', handleNotification);
      webSocketService.on('unread_count', handleUnreadCount);
      webSocketService.on('notifications_list', handleNotificationsList);
      webSocketService.on('error', handleError);

      // Cleanup on unmount or user change
      return () => {
        webSocketService.off('connect', handleConnect);
        webSocketService.off('disconnect', handleDisconnect);
        webSocketService.off('notification', handleNotification);
        webSocketService.off('unread_count', handleUnreadCount);
        webSocketService.off('notifications_list', handleNotificationsList);
        webSocketService.off('error', handleError);
        webSocketService.disconnect();
        setIsConnected(false);
        setNotifications([]);
        setUnreadCount(0);
      };
    } else {
      // Disconnect if user logs out
      webSocketService.disconnect();
      setIsConnected(false);
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user, token]);

  // Request browser notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const markAsRead = async (notificationId: number) => {
    try {
      // Mark as read via WebSocket
      webSocketService.markNotificationAsRead(notificationId);
      
      // Also call the API to ensure consistency
      await api.notifications.markAsRead(notificationId);
      
      // Update local state
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId ? { ...notif, is_read: true } : notif
        )
      );
      
      // Update unread count
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      // Mark all as read via WebSocket
      webSocketService.markAllNotificationsAsRead();
      
      // Also call the API to ensure consistency
      await api.notifications.markAllAsRead();
      
      // Update local state
      setNotifications(prev =>
        prev.map(notif => ({ ...notif, is_read: true }))
      );
      
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const refreshNotifications = async () => {
    try {
      // Request fresh notifications via WebSocket
      webSocketService.getNotifications();
      
      // Also fetch via API as fallback
      const apiNotifications = await api.notifications.getAll();
      setNotifications(apiNotifications);
      
      const unreadResponse = await api.notifications.getUnreadCount();
      setUnreadCount(unreadResponse.count);
    } catch (error) {
      console.error('Error refreshing notifications:', error);
    }
  };

  const value: NotificationsContextType = {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
  };

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
};

export const useNotifications = (): NotificationsContextType => {
  const context = useContext(NotificationsContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationsProvider');
  }
  return context;
};
