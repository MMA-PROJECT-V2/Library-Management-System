import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Service URLs
export const USER_SERVICE_URL = 'http://localhost:8001/api/users';
export const BOOKS_SERVICE_URL = 'http://localhost:8002/api';
export const LOANS_SERVICE_URL = 'http://localhost:8003/api/loans';
export const NOTIFICATIONS_SERVICE_URL = 'http://localhost:8004/api';

// Create axios instance
const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }
        
        const response = await axios.post(
          `${USER_SERVICE_URL}/token/refresh/`,
          { refresh: refreshToken }
        );
        
        const { access, refresh } = response.data;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
