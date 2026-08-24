import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
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
  const [selectedMmsiState, setSelectedMmsiState] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  const requestGenRef = useRef(0);

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
    const currentGen = ++requestGenRef.current;
    setLoading(true);
    setLoadingMessage('Fetching latest TRACE intelligence data...');
    setError(null);
    try {
      const healthRes = await checkHealth();
      if (currentGen !== requestGenRef.current) return;
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

      if (currentGen !== requestGenRef.current) return;

      setIncident(incidentData);
      setVessels(Array.isArray(vesselData) ? vesselData : []);

      // Update LAST UPDATED using timestamp returned by backend
      const backendTime = incidentData?.metadata?.generation_timestamp 
        || incidentData?.spill?.timestamp 
        || fetchCompletionTime;

      setLastUpdated(backendTime);

      // Auto select top candidate MMSI if available
      if (incidentData?.ranked_candidates?.length > 0) {
        setSelectedMmsiState(incidentData.ranked_candidates[0].mmsi);
      } else if (Array.isArray(vesselData) && vesselData.length > 0) {
        setSelectedMmsiState(vesselData[0].mmsi);
      } else {
        setSelectedMmsiState(null);
      }
    } catch (err) {
      if (currentGen !== requestGenRef.current) return;
      console.error('TRACE Data Refresh Error:', err);
      setError(err.message || 'Unable to connect to TRACE backend server.');
    } finally {
      if (currentGen === requestGenRef.current) {
        setLoading(false);
        setLoadingMessage(null);
      }
    }
  }, []);

  const runPipeline = useCallback(async () => {
    const currentGen = ++requestGenRef.current;
    setLoading(true);
    setLoadingMessage('Running TRACE Pipeline Analysis...');
    setError(null);
    try {
      const pipelineExecutionTime = new Date().toISOString();

      // Call real backend pipeline endpoint
      const result = await runPipelineApi();

      if (currentGen !== requestGenRef.current) return;

      if (!result || result.status !== 'success' || !result.incident) {
        throw new Error(result?.message || 'Pipeline execution failed on backend.');
      }

      // Update dashboard data with returned result from backend
      setIncident(result.incident);

      // Fetch optional candidate vessels from backend
      const vesselData = await getCandidateVessels().catch(() => []);
      if (currentGen !== requestGenRef.current) return;
      setVessels(Array.isArray(vesselData) ? vesselData : []);

      // Update LAST UPDATED timestamp
      const pipelineTimestamp = result.incident?.metadata?.generation_timestamp 
        || result.incident?.spill?.timestamp 
        || pipelineExecutionTime;

      setLastUpdated(pipelineTimestamp);

      if (result.incident?.ranked_candidates?.length > 0) {
        setSelectedMmsiState(result.incident.ranked_candidates[0].mmsi);
      }
    } catch (err) {
      if (currentGen !== requestGenRef.current) return;
      console.error('TRACE Pipeline Execution Error:', err);
      setError(err.message || 'Failed to execute TRACE pipeline.');
    } finally {
      if (currentGen === requestGenRef.current) {
        setLoading(false);
        setLoadingMessage(null);
      }
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
  }, [loadData]);

  // Combine attribution score with physical vessel details (memoized)
  const candidates = useMemo(() => {
    if (!incident || !incident.ranked_candidates) return [];

    const activeSpillId = incident.spill?.spill_id;

    return incident.ranked_candidates.map(candidate => {
      // Enforce provenance: only match vessel if spill_id matches active incident
      const physicalVessel = vessels.find(
        v => v.mmsi === candidate.mmsi && (!activeSpillId || v.spill_id === activeSpillId)
      );

      return {
        ...candidate,
        vessel_name: physicalVessel?.vessel_name || candidate.vessel_identity || `Vessel ${candidate.mmsi}`,
        vessel_type: physicalVessel?.vessel_type || 'Unknown Type',
        minimum_distance_km: typeof physicalVessel?.minimum_distance_km === 'number' ? physicalVessel.minimum_distance_km : 'Unavailable',
        source_window_presence: typeof physicalVessel?.source_window_presence === 'boolean' ? physicalVessel.source_window_presence : 'Unknown',
        time_spent_near_source_min: typeof physicalVessel?.time_spent_near_source_min === 'number' ? physicalVessel.time_spent_near_source_min : null,
        average_speed: typeof physicalVessel?.average_speed === 'number' ? physicalVessel.average_speed : null,
        course: typeof physicalVessel?.course === 'number' ? physicalVessel.course : null,
        ais_gap_detected: typeof physicalVessel?.ais_gap_detected === 'boolean' ? physicalVessel.ais_gap_detected : null,
        trajectory: Array.isArray(physicalVessel?.trajectory) ? physicalVessel.trajectory : [],
      };
    });
  }, [incident, vessels]);

  // Derive effective selected MMSI to ensure selected candidate is always valid without synchronous state mutations
  const selectedMmsi = useMemo(() => {
    if (candidates.length === 0) return null;
    if (selectedMmsiState && candidates.some(c => c.mmsi === selectedMmsiState)) {
      return selectedMmsiState;
    }
    return candidates[0].mmsi;
  }, [candidates, selectedMmsiState]);

  const selectedCandidate = useMemo(() => {
    return candidates.find(c => c.mmsi === selectedMmsi) || candidates[0] || null;
  }, [candidates, selectedMmsi]);

  return {
    loading,
    loadingMessage,
    error,
    health,
    incident,
    vessels,
    candidates,
    selectedMmsi,
    setSelectedMmsi: setSelectedMmsiState,
    selectedCandidate,
    lastUpdated,
    refreshData: loadData,
    runPipeline,
    layerVisibility,
    toggleLayer,
  };
}
