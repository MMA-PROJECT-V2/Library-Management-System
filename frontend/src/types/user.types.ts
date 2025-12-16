export type UserRole = 'MEMBER' | 'LIBRARIAN' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  max_loans: number;
  date_joined: string;
  is_staff: boolean;
  is_superuser: boolean;
  permissions: string[];
  groups: string[];
}

export interface UserProfile {
  user: User;
  bio: string;
  address: string;
  avatar_url: string;
  birth_date: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username?: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role?: UserRole;
}

export interface AuthResponse {
  message: string;
  user: User;
  access: string;
  refresh: string;
}

export interface ProfileUpdateRequest {
  bio?: string;
  address?: string;
  avatar_url?: string;
  birth_date?: string;
}
