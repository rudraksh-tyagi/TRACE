/**
 * TRACE Incident API Service
 * Centralized service layer connecting the frontend with the FastAPI backend.
 */

import { fetchApi } from './client';

export async function checkHealth() {
  try {
    const data = await fetchApi('/health');
    return {
      online: true,
      service: data.service || 'trace-backend',
      mockMode: data.mock_mode ?? false,
    };
  } catch {
    return {
      online: false,
      service: 'trace-backend',
      mockMode: false,
    };
  }
}

export async function getCompleteIncident() {
  return await fetchApi('/api/incident/complete');
}

export async function getCandidateVessels() {
  return await fetchApi('/api/vessels');
}

export async function getSpill() {
  return await fetchApi('/api/spill');
}

export async function getDrift() {
  return await fetchApi('/api/drift');
}

export async function getAttribution() {
  try {
    const data = await fetchApi('/api/attribution');
    return { data, isFallback: false };
  } catch {
    return { data: FALLBACK_INCIDENT.ranked_candidates, isFallback: true };
  }
}
