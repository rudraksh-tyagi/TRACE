import { useState, useEffect, useCallback } from 'react';
import { 
  checkHealth, 
  getCompleteIncident, 
  getCandidateVessels, 
  runPipelineApi 
} from '../api/incidentService';

export function useIncidentData() {
  const [loading, setLoading] = useState(true);
  const [loadingMessage, setLoadingMessage] = useState(null);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState({ online: false, mockMode: false });
  const [incident, setIncident] = useState(null);
  const [vessels, setVessels] = useState([]);
  const [selectedMmsi, setSelectedMmsi] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // Layer visibility state for map
  const [layerVisibility, setLayerVisibility] = useState({
    spillPolygon: true,
    spillCentroid: true,
    sourceRegion: true,
    uncertaintyRegion: true,
    backwardDrift: true,
    forwardForecast: true,
    vesselTrajectories: true,
  });

  const toggleLayer = useCallback((layerKey) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layerKey]: !prev[layerKey]
    }));
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    setLoadingMessage('Fetching latest TRACE intelligence data...');
    setError(null);
    try {
      const healthRes = await checkHealth();
      setHealth(healthRes);

      if (!healthRes.online) {
        throw new Error('Unable to connect to TRACE backend server.');
      }

      const fetchCompletionTime = new Date().toISOString();

      // Fetch complete incident and candidate vessels from backend APIs
      const [incidentData, vesselData] = await Promise.all([
        getCompleteIncident(),
        getCandidateVessels().catch(() => [])
      ]);

      setIncident(incidentData);
      setVessels(Array.isArray(vesselData) ? vesselData : []);

      // Update LAST UPDATED using timestamp returned by backend (or fetch completion time fallback)
      const backendTime = incidentData?.metadata?.generation_timestamp 
        || incidentData?.spill?.timestamp 
        || fetchCompletionTime;

      setLastUpdated(backendTime);

      // Auto select top candidate MMSI
      if (incidentData?.ranked_candidates?.length > 0) {
        setSelectedMmsi(incidentData.ranked_candidates[0].mmsi);
      } else if (Array.isArray(vesselData) && vesselData.length > 0) {
        setSelectedMmsi(vesselData[0].mmsi);
      }
    } catch (err) {
      console.error('TRACE Data Refresh Error:', err);
      setError(err.message || 'Unable to connect to TRACE backend server.');
      // IF API FAILS, DO NOT UPDATE LAST UPDATED
    } finally {
      setLoading(false);
      setLoadingMessage(null);
    }
  }, []);

  const runPipeline = useCallback(async () => {
    setLoading(true);
    setLoadingMessage('Running TRACE Pipeline Analysis...');
    setError(null);
    try {
      const pipelineExecutionTime = new Date().toISOString();

      // Call existing real backend pipeline endpoint
      const result = await runPipelineApi();

      if (!result || result.status !== 'success' || !result.incident) {
        throw new Error(result?.message || 'Pipeline execution failed on backend.');
      }

      // Update dashboard data with returned result from backend
      setIncident(result.incident);

      // Fetch candidate vessels from backend
      const vesselData = await getCandidateVessels().catch(() => []);
      setVessels(Array.isArray(vesselData) ? vesselData : []);

      // Update LAST UPDATED from backend pipeline result timestamp (or execution completion time fallback)
      const pipelineTimestamp = result.incident?.metadata?.generation_timestamp 
        || result.incident?.spill?.timestamp 
        || pipelineExecutionTime;

      setLastUpdated(pipelineTimestamp);

      if (result.incident?.ranked_candidates?.length > 0) {
        setSelectedMmsi(result.incident.ranked_candidates[0].mmsi);
      }
    } catch (err) {
      console.error('TRACE Pipeline Execution Error:', err);
      setError(err.message || 'Failed to execute TRACE pipeline.');
      // IF PIPELINE FAILS, DO NOT UPDATE LAST UPDATED
    } finally {
      setLoading(false);
      setLoadingMessage(null);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Combine attribution score with physical vessel details
  const mergedCandidates = useCallback(() => {
    if (!incident || !incident.ranked_candidates) return [];

    return incident.ranked_candidates.map(candidate => {
      const physicalVessel = vessels.find(v => v.mmsi === candidate.mmsi);
      return {
        ...candidate,
        vessel_name: physicalVessel?.vessel_name || candidate.vessel_identity || `Vessel ${candidate.mmsi}`,
        vessel_type: physicalVessel?.vessel_type || 'Unknown Type',
        minimum_distance_km: physicalVessel?.minimum_distance_km ?? (candidate.component_scores?.distance_score != null ? Math.round((100 - candidate.component_scores.distance_score) * 0.5 * 10) / 10 : 'N/A'),
        source_window_presence: physicalVessel?.source_window_presence ?? (candidate.component_scores?.time_compatibility_score > 50),
        time_spent_near_source_min: physicalVessel?.time_spent_near_source_min ?? 0,
        average_speed: physicalVessel?.average_speed ?? 0.0,
        course: physicalVessel?.course ?? 0.0,
        ais_gap_detected: physicalVessel?.ais_gap_detected ?? false,
        trajectory: physicalVessel?.trajectory || [],
      };
    });
  }, [incident, vessels]);

  const selectedCandidate = mergedCandidates().find(c => c.mmsi === selectedMmsi) || mergedCandidates()[0] || null;

  return {
    loading,
    loadingMessage,
    error,
    health,
    incident,
    vessels,
    candidates: mergedCandidates(),
    selectedMmsi,
    setSelectedMmsi,
    selectedCandidate,
    lastUpdated,
    refreshData: loadData,
    runPipeline,
    layerVisibility,
    toggleLayer,
  };
}
