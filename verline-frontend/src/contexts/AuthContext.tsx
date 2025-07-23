import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, api, LoginData, RegisterData } from '@/services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (userData: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('access_token');
      if (storedToken) {
        try {
          // Decode JWT token to get username
          const tokenPayload = JSON.parse(atob(storedToken.split('.')[1]));
          const username = tokenPayload.sub;
          
          // Check if token is expired
          const currentTime = Date.now() / 1000;
          if (tokenPayload.exp < currentTime) {
            // Token is expired, remove it
            localStorage.removeItem('access_token');
            setIsLoading(false);
            return;
          }
          
          setToken(storedToken);
          
          // Fetch all users and find the one with matching username
          const allUsers = await api.users.getAll();
          const currentUser = allUsers.find(user => user.username === username);
          
          if (currentUser) {
            setUser(currentUser);
          } else {
            // User not found, remove invalid token
            localStorage.removeItem('access_token');
          }
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          localStorage.removeItem('access_token');
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (data: LoginData) => {
    try {
      setIsLoading(true);
      const authResponse = await api.auth.login(data);
      
      // Store token
      setToken(authResponse.access_token);
      
      // Decode JWT token to get username
      const tokenPayload = JSON.parse(atob(authResponse.access_token.split('.')[1]));
      const username = tokenPayload.sub;
      
      // Fetch all users and find the one with matching username
      const allUsers = await api.users.getAll();
      const currentUser = allUsers.find(user => user.username === username);
      
      if (!currentUser) {
        throw new Error('User not found after login');
      }
      
      setUser(currentUser);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    try {
      setIsLoading(true);
      const newUser = await api.auth.register(data);
      
      // Auto login after registration
      await login({ username: data.username, password: data.password });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.auth.logout();
    setUser(null);
    setToken(null);
  };

  const updateUser = (userData: User) => {
    setUser(userData);
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
