import { useContext } from 'react';
import { AuthContext } from '../context/auth-context-def';
import { AuthContextValue } from '../types/auth';

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
