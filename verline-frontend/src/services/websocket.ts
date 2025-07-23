// WebSocket service for real-time notifications
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private listeners: Map<string, Function[]> = new Map();
  private userId: number | null = null;
  private token: string | null = null;
  private isConnecting = false;

  constructor() {
    // Initialize listeners map
    this.listeners.set('notification', []);
    this.listeners.set('unread_count', []);
    this.listeners.set('notifications_list', []);
    this.listeners.set('connect', []);
    this.listeners.set('disconnect', []);
    this.listeners.set('error', []);
  }

  connect(userId: number, token: string) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.userId = userId;
    this.token = token;
    this.isConnecting = true;

    const wsUrl = `ws://localhost:8000/ws/${userId}?token=${token}`;
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.clearReconnectTimer();
        this.emit('connect', null);
        
        // Request initial notifications
        this.send({ type: 'get_notifications' });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          this.emit(message.type, message.data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;
        this.emit('disconnect', { code: event.code, reason: event.reason });
        
        // Auto-reconnect if not a manual disconnect
        if (event.code !== 1000 && this.userId && this.token) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.isConnecting = false;
      this.emit('error', error);
    }
  }

  disconnect() {
    this.clearReconnectTimer();
    this.userId = null;
    this.token = null;

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
    }
  }

  // Event listener management
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket event callback:', error);
        }
      });
    }
  }

  private scheduleReconnect() {
    this.clearReconnectTimer();
    
    // Reconnect after 3 seconds
    this.reconnectTimer = setTimeout(() => {
      if (this.userId && this.token) {
        console.log('Attempting to reconnect WebSocket...');
        this.connect(this.userId, this.token);
      }
    }, 3000);
  }

  private clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  // Utility methods for specific actions
  markNotificationAsRead(notificationId: number) {
    this.send({ type: 'mark_read', notification_id: notificationId });
  }

  markAllNotificationsAsRead() {
    this.send({ type: 'mark_all_read' });
  }

  getNotifications() {
    this.send({ type: 'get_notifications' });
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Create a singleton instance
export const webSocketService = new WebSocketService();

// Types for notifications
export interface NotificationData {
  id: number;
  type: string;
  message: string;
  sender: {
    id: number;
    username: string;
    full_name: string;
    profile_picture?: string;
  };
  painting_id?: number;
  comment_id?: number;
  rating_id?: number;
  is_read: boolean;
  created_at: string;
}

export interface UnreadCountData {
  count: number;
}

export default webSocketService;
