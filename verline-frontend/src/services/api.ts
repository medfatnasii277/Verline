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
  rating: number; // 1-5
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  user_id: number;
  user: User;
  painting_id: number;
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

    delete: async (paintingId: number): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/paintings/${paintingId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error(`Failed to delete painting: ${response.statusText}`);
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
};
