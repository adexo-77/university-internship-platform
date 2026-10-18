import React, { useCallback, useEffect, useState } from 'react';
import { getCurrentUser, loginUser, logoutUser, registerUser } from '../api/auth';
import { LoginPayload, RegisterPayload, User } from '../types/auth';
import { AuthContext } from './auth-context-def';

export interface AuthProviderProps {
  children: React.ReactNode;
  initialUser?: User | null;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children, initialUser }) => {
  const [user, setUser] = useState<User | null>(initialUser ?? null);
  const [isLoading, setIsLoading] = useState<boolean>(initialUser === undefined);

  const fetchSession = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialUser === undefined) {
      void fetchSession();
    }
  }, [fetchSession, initialUser]);

  const login = async (payload: LoginPayload): Promise<User> => {
    const authenticatedUser = await loginUser(payload);
    setUser(authenticatedUser);
    return authenticatedUser;
  };

  const register = async (payload: RegisterPayload): Promise<User> => {
    const registeredUser = await registerUser(payload);
    setUser(registeredUser);
    return registeredUser;
  };

  const logout = async (): Promise<void> => {
    try {
      await logoutUser();
    } finally {
      setUser(null);
    }
  };

  const refetchUser = async (): Promise<void> => {
    await fetchSession();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-chalk flex items-center justify-center p-6 text-center">
        <div className="rounded-control border border-line bg-surface p-6 shadow-sm max-w-sm w-full">
          <p className="text-base font-medium text-ink">Checking platform session</p>
          <p className="text-xs text-pencil mt-1">Verifying credentials and permissions...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: false,
        isAuthenticated: user !== null,
        login,
        register,
        logout,
        refetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
