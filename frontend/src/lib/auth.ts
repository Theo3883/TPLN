/**
 * Auth API functions with JWT token handling
 */

import { User, LoginCredentials, RegisterData, TokenResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * Make an authenticated request with JWT token
 */
async function authFetch(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  } as HeadersInit;

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response = await fetch(url, { ...options, headers });

  // If 401, try to refresh token
  if (response.status === 401 && token) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        const newTokens = await refreshAccessToken(refreshToken);
        localStorage.setItem('access_token', newTokens.access_token);
        localStorage.setItem('refresh_token', newTokens.refresh_token);

        // Retry original request with new token
        headers['Authorization'] = `Bearer ${newTokens.access_token}`;
        response = await fetch(url, { ...options, headers });
      } catch (error) {
        // Refresh failed, clear tokens and throw
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw new Error('Session expired. Please login again.');
      }
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Register a new user
 */
export async function register(data: RegisterData): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

/**
 * Login user and get JWT tokens
 */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

/**
 * Refresh access token
 */
export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new Error('Token refresh failed');
  }

  return response.json();
}

/**
 * Logout user (invalidate refresh token)
 */
export async function logout(refreshToken: string): Promise<void> {
  await authFetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  return authFetch(`${API_BASE}/users/me`);
}

/**
 * Update user profile
 */
export async function updateProfile(data: Partial<User>): Promise<User> {
  return authFetch(`${API_BASE}/users/me`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete user account
 */
export async function deleteAccount(): Promise<void> {
  await authFetch(`${API_BASE}/users/me`, {
    method: 'DELETE',
  });
}
