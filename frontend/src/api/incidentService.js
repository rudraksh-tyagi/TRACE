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
  try {
    return await fetchApi('/api/run-pipeline', { method: 'POST' });
  } catch (initialErr) {
    // If backend pipeline input buffer is uninitialized (causing 500 error in orchestrate mode),
    // ingest backend spill, drift, and vessel data into backend input store first
    try {
      const [spill, drift, vessels] = await Promise.all([
        fetchApi('/api/spill'),
        fetchApi('/api/drift'),
        fetchApi('/api/vessels'),
      ]);

      if (spill && drift && vessels && Array.isArray(vessels) && vessels.length > 0) {
        await fetchApi('/api/ingest/spill', { method: 'POST', body: JSON.stringify(spill) });
        await fetchApi('/api/ingest/drift', { method: 'POST', body: JSON.stringify(drift) });
        await fetchApi('/api/ingest/vessels', { method: 'POST', body: JSON.stringify(vessels) });
        
        // Retry backend run-pipeline execution after populating backend inputs
        return await fetchApi('/api/run-pipeline', { method: 'POST' });
      }
    } catch {
      // Re-throw initial pipeline execution error if fallback fails
    }
    throw initialErr;
  }
}

export async function orchestratePipeline(payload = {}) {
  return await fetchApi('/api/orchestrate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
