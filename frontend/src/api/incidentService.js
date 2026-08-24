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
  return await fetchApi('/api/attribution');
}

export async function runPipelineApi() {
  return await fetchApi('/api/run-pipeline', { method: 'POST' });
}

export async function orchestratePipeline(payload = {}) {
  return await fetchApi('/api/orchestrate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
