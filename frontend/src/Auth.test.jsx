import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter, Route, Routes } from 'react-router-dom';

import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';
import { authApi } from './services/api';

vi.mock('./services/api', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    logout: vi.fn(),
  },
  healthApi: {
    checkHealth: vi.fn(),
    checkReady: vi.fn(),
  },
}));

describe('Frontend Authentication Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login form and handles successful submission', async () => {
    authApi.login.mockResolvedValue({
      data: {
        access_token: 'fake-jwt-token-xyz',
        user: { id: 1, name: 'Admin User', email: 'admin@example.com', role: 'admin' },
      },
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByPlaceholderText(/admin@example.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/admin@example.com/i), {
      target: { value: 'admin@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: 'AdminPass123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'admin@example.com',
        password: 'AdminPass123!',
      });
      expect(localStorage.getItem('auth_token')).toBe('fake-jwt-token-xyz');
    });
  });

  it('displays error message on invalid credentials during login', async () => {
    authApi.login.mockRejectedValue({
      message: 'Incorrect email or password.',
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/admin@example.com/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: 'WrongPass!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/incorrect email or password/i)).toBeInTheDocument();
    });
  });

  it('validates password length on registration form', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Register />
        </AuthProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Jane Doe/i), {
      target: { value: 'Alice' },
    });
    fireEvent.change(screen.getByPlaceholderText(/jane.doe@example.com/i), {
      target: { value: 'alice@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText(/At least 8 characters/i), {
      target: { value: 'short' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('protects routes and redirects unauthenticated users to /login', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page Screen</div>} />
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<div>Secret Dashboard</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page Screen')).toBeInTheDocument();
    expect(screen.queryByText('Secret Dashboard')).not.toBeInTheDocument();
  });
});
