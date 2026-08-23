import { useState, useEffect, useCallback } from 'react';
import { checkHealth, getCompleteIncident, getCandidateVessels } from '../api/incidentService';

export function useIncidentData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState({ online: false, mockMode: true });
  const [incident, setIncident] = useState(null);
  const [vessels, setVessels] = useState([]);
  const [selectedMmsi, setSelectedMmsi] = useState(null);
  const [isFallback, setIsFallback] = useState(false);
  
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

      const [incidentRes, vesselsRes] = await Promise.all([
        getCompleteIncident(),
        getCandidateVessels()
      ]);

      setIncident(incidentRes.data);
      setVessels(vesselsRes.data || []);
      setIsFallback(incidentRes.isFallback || vesselsRes.isFallback);

      // Auto select top candidate MMSI
      if (incidentRes.data?.ranked_candidates?.length > 0) {
        setSelectedMmsi(incidentRes.data.ranked_candidates[0].mmsi);
      } else if (vesselsRes.data?.length > 0) {
        setSelectedMmsi(vesselsRes.data[0].mmsi);
      }
    } catch (err) {
      console.error('Failed to load incident data:', err);
      setError(err.message || 'Unable to connect to TRACE backend server.');
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
        vessel_name: physicalVessel?.vessel_name || candidate.vessel_identity?.split(' ')[0] || 'Vessel ' + candidate.mmsi.slice(-3),
        vessel_type: physicalVessel?.vessel_type || 'Tanker',
        minimum_distance_km: physicalVessel?.minimum_distance_km ?? 12.4,
        source_window_presence: physicalVessel?.source_window_presence ?? true,
        time_spent_near_source_min: physicalVessel?.time_spent_near_source_min ?? 0,
        average_speed: physicalVessel?.average_speed ?? 10.0,
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
    isFallback,
    refreshData: loadData,
    layerVisibility,
    toggleLayer,
  };
}
