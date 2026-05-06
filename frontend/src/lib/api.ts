const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function handleResponse(resp: Response) {
  const text = await resp.text();
  try {
    return JSON.parse(text || '{}');
  } catch {
    return text;
  }
}

export async function listEditions(limit = 90) {
  const res = await fetch(`${API_BASE}/editions?limit=${limit}`);
  if (!res.ok) throw new Error(`listEditions failed: ${res.status}`);
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

export async function createReview(payload: any) {
  const res = await fetch(`${API_BASE}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`createReview failed: ${res.status}`);
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

export async function getAudit(editionId: number | string) {
  const res = await fetch(`${API_BASE}/audit/editions/${editionId}`);
  if (!res.ok) throw new Error(`getAudit failed: ${res.status}`);
  return handleResponse(res);
}

export default {
  listEditions,
  getEdition,
  searchEditions,
  listRankings,
  getEditionReviews,
  listPendingReviews,
  createReview,
  approveReview,
  rejectReview,
  getAudit,
};
