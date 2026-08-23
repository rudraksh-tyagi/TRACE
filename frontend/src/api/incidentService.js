/**
 * TRACE Incident API Service
 * Wraps backend endpoints with fallback handling for demo resilience
 */

import { fetchApi } from './client';
import { FALLBACK_INCIDENT, FALLBACK_VESSELS } from './fallbackData';

export async function checkHealth() {
  try {
    const data = await fetchApi('/health');
    return {
      online: true,
      service: data.service || 'trace-backend',
      mockMode: data.mock_mode ?? true,
    };
  } catch {
    return {
      online: false,
      service: 'trace-backend',
      mockMode: true,
    };
  }
}

export async function getCompleteIncident() {
  try {
    const data = await fetchApi('/api/incident/complete');
    return { data, isFallback: false };
  } catch {
    console.warn('Backend API unavailable for /api/incident/complete. Using local static demonstration fallback.');
    return { data: FALLBACK_INCIDENT, isFallback: true };
  }
}

export async function getCandidateVessels() {
  try {
    const data = await fetchApi('/api/vessels');
    return { data, isFallback: false };
  } catch {
    console.warn('Backend API unavailable for /api/vessels. Using local static demonstration fallback.');
    return { data: FALLBACK_VESSELS, isFallback: true };
  }
}

export async function getSpill() {
  try {
    const data = await fetchApi('/api/spill');
    return { data, isFallback: false };
  } catch {
    return { data: FALLBACK_INCIDENT.spill, isFallback: true };
  }
}

export async function getDrift() {
  try {
    const data = await fetchApi('/api/drift');
    return { data, isFallback: false };
  } catch {
    return { data: FALLBACK_INCIDENT.drift, isFallback: true };
  }
}

export async function getAttribution() {
  try {
    const data = await fetchApi('/api/attribution');
    return { data, isFallback: false };
  } catch {
    return { data: FALLBACK_INCIDENT.ranked_candidates, isFallback: true };
  }
}
