/**
 * User roles in the platform.
 */
export type UserRole = 'student' | 'instructor' | 'organization' | 'admin' | 'coordinator';

/**
 * Roles allowed for self-service public registration.
 */
export type PublicRegisterRole = 'student' | 'organization';

/**
 * Authenticated user profile representation.
 */
export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Payload for public user registration.
 */
export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role: PublicRegisterRole;
  organization_name?: string;
}

/**
 * Payload for credentials login.
 */
export interface LoginPayload {
  email: string;
  password: string;
}

/**
 * Payload for changing password.
 */
export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

/**
 * Context state for authentication.
 */
export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

/**
 * Context interface including action methods.
 */
export interface AuthContextValue extends AuthState {
  login: (payload: LoginPayload) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => Promise<void>;
  refetchUser: () => Promise<void>;
}
