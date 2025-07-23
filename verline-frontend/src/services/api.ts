// API service layer for backend communication
const API_BASE_URL = 'http://localhost:8000';

// Types based on backend schemas
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'artist' | 'enthusiast';
  bio?: string;
  profile_picture?: string;
  location?: string;
  website?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Painting {
  id: number;
  title: string;
  description?: string;
  artist_id: number;
  artist: User;
  category_id?: number;
  category?: Category;
  image_url: string;
  thumbnail_url?: string;
  price?: number;
  year_created?: number;
  dimensions?: string;
  medium?: string;
  status: 'draft' | 'published' | 'archived';
  view_count: number;
  average_rating?: number;
  rating_count: number;
  tags?: string;
  created_at: string;
  updated_at: string;
}

export interface Rating {
  id: number;
  user_id: number;
  user: User;
  painting_id: number;
  painting?: Painting;
  rating: number; // 1-5
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  user_id: number;
  user: User;
  painting_id: number;
  painting?: Painting;
  content: string;
  parent_id?: number;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

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

export interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  password: string;
  role: 'artist' | 'enthusiast';
  bio?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// API functions
export const api = {
  // Authentication
  auth: {
    register: async (data: RegisterData): Promise<User> => {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`Registration failed: ${response.statusText}`);
      return response.json();
    },

    login: async (data: LoginData): Promise<AuthResponse> => {
      const formData = new FormData();
      formData.append('username', data.username);
      formData.append('password', data.password);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(`Login failed: ${response.statusText}`);
      const authData = await response.json();
      
      // Store token
      localStorage.setItem('access_token', authData.access_token);
      return authData;
    },

    logout: () => {
      localStorage.removeItem('access_token');
    },
  },

  // Users
  users: {
    getAll: async (): Promise<User[]> => {
      const response = await fetch(`${API_BASE_URL}/users/`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to fetch users: ${response.statusText}`);
      return response.json();
    },

    getArtists: async (): Promise<User[]> => {
      const response = await fetch(`${API_BASE_URL}/users/artists`);
      if (!response.ok) throw new Error(`Failed to fetch artists: ${response.statusText}`);
      return response.json();
    },

    getById: async (userId: number): Promise<User> => {
      const response = await fetch(`${API_BASE_URL}/users/${userId}`);
      if (!response.ok) throw new Error(`Failed to fetch user: ${response.statusText}`);
      return response.json();
    },

    updateProfile: async (userId: number, data: Partial<User>): Promise<User> => {
      const response = await fetch(`${API_BASE_URL}/users/me/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`Failed to update profile: ${response.statusText}`);
      return response.json();
    },

    // Alias for consistency with frontend usage
    update: async (userId: number, data: Partial<User>): Promise<User> => {
      return api.users.updateProfile(userId, data);
    },

    uploadProfilePicture: async (userId: number, file: File): Promise<User> => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/users/me/${userId}/profile-picture`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });
      
      if (!response.ok) throw new Error(`Failed to upload profile picture: ${response.statusText}`);
      return response.json();
    },

    getUserPaintings: async (userId: number, page = 1, limit = 20): Promise<PaginatedResponse<Painting>> => {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/paintings?page=${page}&limit=${limit}`);
      if (!response.ok) throw new Error(`Failed to fetch user paintings: ${response.statusText}`);
      return response.json();
    },
  },

  // Paintings
  paintings: {
    getAll: async (page = 1, limit = 20, categoryId?: number): Promise<PaginatedResponse<Painting>> => {
      const params = new URLSearchParams({
        skip: ((page - 1) * limit).toString(),
        limit: limit.toString(),
      });
      if (categoryId) params.append('category_id', categoryId.toString());

      const response = await fetch(`${API_BASE_URL}/paintings/?${params}`);
      if (!response.ok) throw new Error(`Failed to fetch paintings: ${response.statusText}`);
      return response.json();
    },

    getById: async (paintingId: number): Promise<Painting> => {
      const response = await fetch(`${API_BASE_URL}/paintings/${paintingId}`);
      if (!response.ok) throw new Error(`Failed to fetch painting: ${response.statusText}`);
      return response.json();
    },

    getMyPaintings: async (artistId: number, page = 1, limit = 20): Promise<PaginatedResponse<Painting>> => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });

      const response = await fetch(`${API_BASE_URL}/paintings/my-paintings/${artistId}?${params}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to fetch my paintings: ${response.statusText}`);
      return response.json();
    },

    create: async (data: FormData): Promise<Painting> => {
      const response = await fetch(`${API_BASE_URL}/paintings/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: data,
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Painting creation failed:', response.status, errorData);
        throw new Error(`Failed to create painting: ${response.status} ${response.statusText} - ${errorData}`);
      }
      return response.json();
    },

    update: async (paintingId: number, data: FormData): Promise<Painting> => {
      const response = await fetch(`${API_BASE_URL}/paintings/${paintingId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: data,
      });
      if (!response.ok) throw new Error(`Failed to update painting: ${response.statusText}`);
      return response.json();
    },

    delete: async (paintingId: number, artistId: number): Promise<void> => {
      console.log('Deleting painting with ID:', paintingId, 'by artist:', artistId);
      console.log('Auth headers:', getAuthHeaders());
      
      const response = await fetch(`${API_BASE_URL}/paintings/${paintingId}?artist_id=${artistId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      
      console.log('Delete response status:', response.status);
      console.log('Delete response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Delete error response:', errorText);
        throw new Error(`Failed to delete painting: ${response.statusText} - ${errorText}`);
      }
      
      console.log('Painting deleted successfully');
    },
  },

  // Categories
  categories: {
    getAll: async (): Promise<Category[]> => {
      const response = await fetch(`${API_BASE_URL}/categories/`);
      if (!response.ok) throw new Error(`Failed to fetch categories: ${response.statusText}`);
      return response.json();
    },

    getById: async (categoryId: number): Promise<Category> => {
      const response = await fetch(`${API_BASE_URL}/categories/${categoryId}`);
      if (!response.ok) throw new Error(`Failed to fetch category: ${response.statusText}`);
      return response.json();
    },

    create: async (data: { name: string; description?: string }): Promise<Category> => {
      const response = await fetch(`${API_BASE_URL}/categories/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`Failed to create category: ${response.statusText}`);
      return response.json();
    },
  },

  // Ratings
  ratings: {
    create: async (paintingId: number, rating: number): Promise<Rating> => {
      const response = await fetch(`${API_BASE_URL}/ratings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ painting_id: paintingId, rating }),
      });
      if (!response.ok) throw new Error(`Failed to create rating: ${response.statusText}`);
      return response.json();
    },

    getMyRatings: async (): Promise<Rating[]> => {
      const response = await fetch(`${API_BASE_URL}/ratings/my-ratings`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to fetch my ratings: ${response.statusText}`);
      return response.json();
    },

    getMyPaintingsRatings: async (): Promise<Rating[]> => {
      const response = await fetch(`${API_BASE_URL}/ratings/my-paintings-ratings`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to fetch my paintings ratings: ${response.statusText}`);
      return response.json();
    },

    getPaintingRatings: async (paintingId: number): Promise<Rating[]> => {
      const response = await fetch(`${API_BASE_URL}/ratings/painting/${paintingId}`);
      if (!response.ok) throw new Error(`Failed to fetch painting ratings: ${response.statusText}`);
      return response.json();
    },

    getPaintingAverage: async (paintingId: number): Promise<{ average_rating: number; rating_count: number }> => {
      const response = await fetch(`${API_BASE_URL}/ratings/painting/${paintingId}/average`);
      if (!response.ok) throw new Error(`Failed to fetch painting average: ${response.statusText}`);
      return response.json();
    },

    update: async (ratingId: number, rating: number): Promise<Rating> => {
      const response = await fetch(`${API_BASE_URL}/ratings/${ratingId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ rating }),
      });
      if (!response.ok) throw new Error(`Failed to update rating: ${response.statusText}`);
      return response.json();
    },

    delete: async (ratingId: number): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/ratings/${ratingId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to delete rating: ${response.statusText}`);
    },
  },

  // Comments
  comments: {
    create: async (paintingId: number, userId: number, content: string, parentId?: number): Promise<Comment> => {
      const response = await fetch(`${API_BASE_URL}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ 
          painting_id: paintingId, 
          user_id: userId,
          content, 
          parent_id: parentId 
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Comment creation failed:', response.status, errorData);
        throw new Error(`Failed to create comment: ${response.status} ${response.statusText} - ${errorData}`);
      }
      return response.json();
    },

    getPaintingComments: async (paintingId: number): Promise<Comment[]> => {
      const response = await fetch(`${API_BASE_URL}/comments/painting/${paintingId}`);
      if (!response.ok) throw new Error(`Failed to fetch painting comments: ${response.statusText}`);
      return response.json();
    },

    getUserComments: async (userId: number): Promise<Comment[]> => {
      const response = await fetch(`${API_BASE_URL}/comments/user/${userId}`);
      if (!response.ok) throw new Error(`Failed to fetch user comments: ${response.statusText}`);
      return response.json();
    },

    getMyPaintingsComments: async (): Promise<Comment[]> => {
      const response = await fetch(`${API_BASE_URL}/comments/my-paintings-comments`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to fetch my paintings comments: ${response.statusText}`);
      return response.json();
    },

    update: async (commentId: number, content: string): Promise<Comment> => {
      const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ content }),
      });
      if (!response.ok) throw new Error(`Failed to update comment: ${response.statusText}`);
      return response.json();
    },

    delete: async (commentId: number): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to delete comment: ${response.statusText}`);
    },
  },

  // Notifications
  notifications: {
    getAll: async (limit: number = 20, offset: number = 0, unreadOnly: boolean = false): Promise<NotificationData[]> => {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        unread_only: unreadOnly.toString(),
      });
      
      const response = await fetch(`${API_BASE_URL}/notifications/?${params}`, {
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) throw new Error(`Failed to fetch notifications: ${response.statusText}`);
      return response.json();
    },

    getUnreadCount: async (): Promise<{ count: number }> => {
      const response = await fetch(`${API_BASE_URL}/notifications/unread-count`, {
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) throw new Error(`Failed to fetch unread count: ${response.statusText}`);
      return response.json();
    },

    markAsRead: async (notificationId: number): Promise<{ message: string }> => {
      const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) throw new Error(`Failed to mark notification as read: ${response.statusText}`);
      return response.json();
    },

    markAllAsRead: async (): Promise<{ message: string }> => {
      const response = await fetch(`${API_BASE_URL}/notifications/mark-all-read`, {
        method: 'PUT',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) throw new Error(`Failed to mark all notifications as read: ${response.statusText}`);
      return response.json();
    },
  },
};
