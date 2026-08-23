import React from 'react';
import { Ship, Navigation, Gauge, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

export function VesselSpotlightCard({ vessel }) {
  if (!vessel) return null;

  return (
    <div className="vessel-spotlight-card">
      <div className="card-top">
        <div className="vessel-title-group">
          <Ship size={18} className="vessel-icon" />
          <div>
            <h4 className="vessel-name">{vessel.vessel_name}</h4>
            <span className="vessel-sub">MMSI: {vessel.mmsi} • {vessel.vessel_type}</span>
          </div>
        </div>
        <div className="vessel-score-pill">
          <span className="score-label">Compatibility Score</span>
          <span className="score-val">{vessel.overall_score}%</span>
        </div>
      </div>

      <div className="vessel-features-grid">
        <div className="feature-item">
          <Navigation size={13} className="feature-icon" />
          <span className="feature-label">Min Distance to Origin</span>
          <span className="feature-val">{typeof vessel.minimum_distance_km === 'number' ? `${vessel.minimum_distance_km} km` : vessel.minimum_distance_km}</span>
        </div>

        <div className="feature-item">
          <Gauge size={13} className="feature-icon" />
          <span className="feature-label">Average Speed</span>
          <span className="feature-val">{vessel.average_speed != null ? `${vessel.average_speed} knots` : 'N/A'}</span>
        </div>

        <div className="feature-item">
          <Navigation size={13} className="feature-icon" />
          <span className="feature-label">Mean Course</span>
          <span className="feature-val">{vessel.course != null ? `${vessel.course}°` : 'N/A'}</span>
        </div>

        <div className="feature-item">
          <Clock size={13} className="feature-icon" />
          <span className="feature-label">Time Near Source</span>
          <span className="feature-val">{vessel.time_spent_near_source_min != null ? `${vessel.time_spent_near_source_min} min` : 'N/A'}</span>
        </div>
      </div>

      {vessel.ais_gap_detected && (
        <div className="ais-gap-warning">
          <AlertTriangle size={14} className="warning-icon" />
          <span>AIS Gap Anomaly Detected during source time window.</span>
        </div>
      )}
    </div>
  );
}
