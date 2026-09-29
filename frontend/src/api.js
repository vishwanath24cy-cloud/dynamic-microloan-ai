/**
 * API service for communicating with FastAPI backend.
 */
const API_BASE = 'http://localhost:8000';

async function fetchJson(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorBody || res.statusText}`);
  }
  return await res.json();
}

export const api = {
  getHealth: () => fetchJson('/health'),
  getDashboardSummary: () => fetchJson('/api/dashboard/summary'),
  getBorrowers: () => fetchJson('/api/borrowers'),
  getBorrowerDetail: (id) => fetchJson(`/api/borrowers/${id}`),
  getBorrowerRecommendation: (id) => fetchJson(`/api/borrowers/${id}/recommendation`),
  getBorrowerTransactions: (id) => fetchJson(`/api/borrowers/${id}/transactions`),
  getBorrowerCashflow: (id) => fetchJson(`/api/borrowers/${id}/cashflow-prediction`),
  getBorrowerStress: (id) => fetchJson(`/api/borrowers/${id}/stress`),
};
