import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const verifySession = async () => {
      const storedToken = localStorage.getItem('auth_token');
      if (!storedToken) {
        if (isMounted) setLoading(false);
        return;
      }

      try {
        const res = await authApi.getMe();
        if (isMounted) {
          setUser(res.data);
          localStorage.setItem('auth_user', JSON.stringify(res.data));
        }
      } catch (err) {
        if (isMounted) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          setToken(null);
          setUser(null);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    verifySession();
    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    const res = await authApi.login({ email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('auth_token', access_token);
    localStorage.setItem('auth_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (userData) => {
    const res = await authApi.register(userData);
    const { access_token, user: newUserData } = res.data;
    localStorage.setItem('auth_token', access_token);
    localStorage.setItem('auth_user', JSON.stringify(newUserData));
    setToken(access_token);
    setUser(newUserData);
    return newUserData;
  };

  const logout = async () => {
    try {
      if (token) {
        await authApi.logout();
      }
    } catch {
      // Discard token locally regardless of network outcome
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      setToken(null);
      setUser(null);
    }
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (typeof roles === 'string') return user.role === roles;
    if (Array.isArray(roles)) return roles.includes(user.role);
    return false;
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
