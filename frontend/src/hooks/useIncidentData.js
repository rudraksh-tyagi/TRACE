import { useState, useEffect, useCallback } from 'react';
import { checkHealth, getCompleteIncident, getCandidateVessels } from '../api/incidentService';

export function useIncidentData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState({ online: false, mockMode: false });
  const [incident, setIncident] = useState(null);
  const [vessels, setVessels] = useState([]);
  const [selectedMmsi, setSelectedMmsi] = useState(null);
  
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
    setError(null);
    try {
      const healthRes = await checkHealth();
      setHealth(healthRes);

      if (!healthRes.online) {
        throw new Error('Unable to connect to TRACE backend server.');
      }

      // Fetch incident data and vessels in parallel
      const [incidentData, vesselData] = await Promise.all([
        getCompleteIncident(),
        getCandidateVessels().catch(() => []) // vessels endpoint is optional fallback if incident state is complete
      ]);

      setIncident(incidentData);
      setVessels(Array.isArray(vesselData) ? vesselData : []);

      // Auto select top candidate MMSI
      if (incidentData?.ranked_candidates?.length > 0) {
        setSelectedMmsi(incidentData.ranked_candidates[0].mmsi);
      } else if (Array.isArray(vesselData) && vesselData.length > 0) {
        setSelectedMmsi(vesselData[0].mmsi);
      }
    } catch (err) {
      console.error('TRACE Data Load Error:', err);
      setError(err.message || 'Unable to connect to TRACE backend server.');
      setIncident(null);
      setVessels([]);
    } finally {
      setLoading(false);
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
        minimum_distance_km: physicalVessel?.minimum_distance_km ?? candidate.component_scores?.distance_score != null ? Math.round((100 - candidate.component_scores.distance_score) * 0.5 * 10) / 10 : 'N/A',
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
    error,
    health,
    incident,
    vessels,
    candidates: mergedCandidates(),
    selectedMmsi,
    setSelectedMmsi,
    selectedCandidate,
    refreshData: loadData,
    layerVisibility,
    toggleLayer,
  };
}

