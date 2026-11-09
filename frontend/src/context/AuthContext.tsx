'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import {
  UserProfile,
  clearAuthTokens,
  getMe,
  getStoredAccessToken,
  getStoredRefreshToken,
  login as apiLogin,
  logoutUser as apiLogout,
  register as apiRegister,
  saveAuthTokens,
} from '@/lib/api';

interface AuthContextValue {
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<UserProfile>;
  register: (username: string, email: string, password: string) => Promise<UserProfile>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<UserProfile | null>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const initializedRef = useRef(false);

  const refreshUser = useCallback(async (): Promise<UserProfile | null> => {
    const storedToken = getStoredAccessToken();
    const storedRefresh = getStoredRefreshToken();
    if (!storedToken) {
      setUser(null);
      setToken(null);
      setRefreshToken(null);
      setIsLoading(false);
      return null;
    }

    try {
      const profile = await getMe(storedToken);
      const latestToken = getStoredAccessToken() || storedToken;
      saveAuthTokens(latestToken, storedRefresh, profile.role);
      setUser(profile);
      setToken(latestToken);
      setRefreshToken(getStoredRefreshToken());
      setIsLoading(false);
      return profile;
    } catch {
      clearAuthTokens();
      setUser(null);
      setToken(null);
      setRefreshToken(null);
      setIsLoading(false);
      return null;
    }
  }, []);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    // Khởi tạo phiên bất đồng bộ để tuân thủ React 19
    void Promise.resolve().then(() => refreshUser());
  }, [refreshUser]);

  const login = useCallback(async (username: string, password: string): Promise<UserProfile> => {
    const tokenData = await apiLogin(username, password);
    const profile = await getMe(tokenData.access_token);
    saveAuthTokens(tokenData.access_token, tokenData.refresh_token, profile.role);
    setToken(tokenData.access_token);
    setRefreshToken(tokenData.refresh_token || null);
    setUser(profile);
    return profile;
  }, []);

  const register = useCallback(
    async (username: string, email: string, password: string): Promise<UserProfile> => {
      await apiRegister(username, email, password);
      return login(username, password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
    setToken(null);
    setRefreshToken(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        refreshToken,
        isAuthenticated: Boolean(user && token),
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth phải được sử dụng bên trong <AuthProvider>');
  }
  return ctx;
}
