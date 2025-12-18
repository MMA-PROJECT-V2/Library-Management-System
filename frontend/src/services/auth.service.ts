import api, { USER_SERVICE_URL } from './api';
import { rabbitMQService } from './rabbitmq.service';
import type { LoginRequest, RegisterRequest, AuthResponse, UserProfile, ProfileUpdateRequest, User } from '@/types/user.types';

export const authService = {
  register: (data: RegisterRequest) => {
    // Async registration via RabbitMQ
    rabbitMQService.sendToExchange('user.create', data);
    return Promise.resolve({ message: 'Registration queued' });
  },

  login: (data: LoginRequest) =>
    api.post<AuthResponse>(`${USER_SERVICE_URL}/login/`, data),

  refreshToken: (refresh: string) =>
    api.post<{ access: string; refresh: string }>(`${USER_SERVICE_URL}/token/refresh/`, { refresh }),

  getMe: () =>
    api.get<{ user: User }>(`${USER_SERVICE_URL}/me/`),

  getProfile: () =>
    api.get<UserProfile>(`${USER_SERVICE_URL}/profile/`),

  updateProfile: (data: ProfileUpdateRequest) =>
    api.put<UserProfile>(`${USER_SERVICE_URL}/profile/`, data),
};
