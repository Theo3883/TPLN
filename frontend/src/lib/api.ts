const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

import type { ReviewCreate, Review, LikeResponse, TopReview, UnlockedBook, UnlockStatus, PreviewBook, PreviewBookReview } from '../types';

async function handleResponse(resp: Response) {
  const text = await resp.text();
  try {
    return JSON.parse(text || '{}');
  } catch {
    return text;
  }
}

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
        // Import auth functions dynamically to avoid circular dependency
        const { refreshAccessToken } = await import('./auth');
        const newTokens = await refreshAccessToken(refreshToken);
        localStorage.setItem('access_token', newTokens.access_token);
        localStorage.setItem('refresh_token', newTokens.refresh_token);

        // Retry original request with new token
        headers['Authorization'] = `Bearer ${newTokens.access_token}`;
        response = await fetch(url, { ...options, headers });
      } catch (error) {
        // Refresh failed, clear tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw new Error('Session expired. Please login again.');
      }
    }
  }

  return response;
}

export async function listEditions(limit = 90) {
  const res = await fetch(`${API_BASE}/editions?limit=${limit}`);
  if (!res.ok) throw new Error(`listEditions failed: ${res.status}`);
  return handleResponse(res);
}

export async function listEditionsFiltered(filters?: {
  source?: 'manual' | 'crawler';
  crawler_name?: 'bookzone' | 'carturesti' | 'libris';
  skip?: number;
  limit?: number;
}) {
  const params = new URLSearchParams();
  if (filters?.source) params.append('source', filters.source);
  if (filters?.crawler_name) params.append('crawler_name', filters.crawler_name);
  if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
  if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
  
  const res = await fetch(`${API_BASE}/editions?${params.toString()}`);
  if (!res.ok) throw new Error(`listEditionsFiltered failed: ${res.status}`);
  return handleResponse(res);
}

export async function getEdition(id: number | string) {
  const res = await fetch(`${API_BASE}/editions/${id}`);
  if (!res.ok) throw new Error(`getEdition failed: ${res.status}`);
  return handleResponse(res);
}

export async function searchEditions(query: string, params = {}) {
  const q = new URLSearchParams({ q: query, ...params } as any);
  const res = await fetch(`${API_BASE}/search/editions?${q.toString()}`);
  if (!res.ok) throw new Error(`searchEditions failed: ${res.status}`);
  return handleResponse(res);
}

export async function listRankings(limit = 60) {
  const res = await fetch(`${API_BASE}/rankings?limit=${limit}`);
  if (!res.ok) throw new Error(`listRankings failed: ${res.status}`);
  return handleResponse(res);
}

export async function getEditionReviews(id: number | string) {
  const res = await fetch(`${API_BASE}/editions/${id}/reviews`);
  if (!res.ok) throw new Error(`getEditionReviews failed: ${res.status}`);
  return handleResponse(res);
}

export async function listPendingReviews() {
  const res = await fetch(`${API_BASE}/moderation/pending`);
  if (!res.ok) throw new Error(`listPendingReviews failed: ${res.status}`);
  return handleResponse(res);
}

export async function createReview(payload: ReviewCreate): Promise<Review> {
  const res = await authFetch(`${API_BASE}/reviews`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const error = await handleResponse(res);
    throw new Error(error.detail || `createReview failed: ${res.status}`);
  }
  return handleResponse(res);
}

export async function approveReview(id: number | string) {
  const res = await fetch(`${API_BASE}/moderation/${id}/approve`, { method: 'POST' });
  if (!res.ok) throw new Error(`approveReview failed: ${res.status}`);
  return handleResponse(res);
}

export async function rejectReview(id: number | string) {
  const res = await fetch(`${API_BASE}/moderation/${id}/reject`, { method: 'POST' });
  if (!res.ok) throw new Error(`rejectReview failed: ${res.status}`);
  return handleResponse(res);
}

// --- Gamification: Likes & Unlocks ---

export async function likeReview(reviewId: number): Promise<LikeResponse> {
  const res = await authFetch(`${API_BASE}/reviews/${reviewId}/like`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await handleResponse(res);
    throw new Error(error.detail || `likeReview failed: ${res.status}`);
  }
  return handleResponse(res);
}

export async function unlikeReview(reviewId: number): Promise<LikeResponse> {
  const res = await authFetch(`${API_BASE}/reviews/${reviewId}/like`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const error = await handleResponse(res);
    throw new Error(error.detail || `unlikeReview failed: ${res.status}`);
  }
  return handleResponse(res);
}

export async function getTopReview(editionId: number): Promise<TopReview | null> {
  const res = await fetch(`${API_BASE}/editions/${editionId}/top-review`);
  if (!res.ok) throw new Error(`getTopReview failed: ${res.status}`);
  return handleResponse(res);
}

export async function checkEditionUnlocked(editionId: number): Promise<UnlockStatus> {
  const res = await authFetch(`${API_BASE}/editions/${editionId}/is-unlocked`);
  if (!res.ok) throw new Error(`checkEditionUnlocked failed: ${res.status}`);
  return handleResponse(res);
}

export async function getUnlockedBooks(): Promise<UnlockedBook[]> {
  const res = await authFetch(`${API_BASE}/unlocked-books`);
  if (!res.ok) throw new Error(`getUnlockedBooks failed: ${res.status}`);
  return handleResponse(res);
}

export async function getAudit(editionId: number | string) {
  const res = await fetch(`${API_BASE}/audit/editions/${editionId}`);
  if (!res.ok) throw new Error(`getAudit failed: ${res.status}`);
  return handleResponse(res);
}

// --- Preview Books ---

export async function listPreviewBooks(): Promise<PreviewBook[]> {
  const res = await fetch(`${API_BASE}/preview-books`);
  if (!res.ok) throw new Error(`listPreviewBooks failed: ${res.status}`);
  return handleResponse(res);
}

export function getPreviewBookCoverUrl(slug: string): string {
  return `${API_BASE}/preview-books/${slug}/cover`;
}

export function getPreviewBookPdfUrl(slug: string): string {
  return `${API_BASE}/preview-books/${slug}/preview`;
}

export function getFullBookPdfUrl(slug: string): string {
  return `${API_BASE}/preview-books/${slug}/full`;
}

export async function getPreviewBookReviews(slug: string): Promise<PreviewBookReview[]> {
  const res = await fetch(`${API_BASE}/preview-books/${slug}/reviews`);
  if (!res.ok) throw new Error(`getPreviewBookReviews failed: ${res.status}`);
  return handleResponse(res);
}

export async function createPreviewBookReview(
  slug: string,
  payload: { content: string; rating?: number }
): Promise<PreviewBookReview> {
  const res = await authFetch(`${API_BASE}/preview-books/${slug}/reviews`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const error = await handleResponse(res);
    throw new Error(error.detail || `createPreviewBookReview failed: ${res.status}`);
  }
  return handleResponse(res);
}

export default {
  listEditions,
  listEditionsFiltered,
  getEdition,
  searchEditions,
  listRankings,
  getEditionReviews,
  listPendingReviews,
  createReview,
  approveReview,
  rejectReview,
  likeReview,
  unlikeReview,
  getTopReview,
  checkEditionUnlocked,
  getUnlockedBooks,
  getAudit,
  listPreviewBooks,
  getPreviewBookCoverUrl,
  getPreviewBookPdfUrl,
  getFullBookPdfUrl,
  getPreviewBookReviews,
  createPreviewBookReview,
};
