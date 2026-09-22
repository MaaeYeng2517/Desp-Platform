'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { api, clearAuthClientState, setCsrfToken } from '@/lib/api/client';
import type { TokenResponse, User } from '@/lib/types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const response = await api.get<User>('/api/v1/auth/me');
      setUser(response.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  useEffect(() => onAuthChange(refreshUser), [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await api.post<TokenResponse>('/api/v1/auth/login', {
      email,
      password,
    });
    setCsrfToken(response.data.csrf_token);
    setUser(response.data.user);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const response = await api.post<TokenResponse>('/api/v1/auth/register', {
        email,
        password,
        full_name: fullName || undefined,
      });
      setCsrfToken(response.data.csrf_token);
      setUser(response.data.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await api.post('/api/v1/auth/logout');
    } finally {
      clearAuthClientState();
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser }),
    [user, loading, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
