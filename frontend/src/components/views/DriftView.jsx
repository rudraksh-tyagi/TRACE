import React from 'react';
import { Wind, Target, Clock, Compass, Navigation, Layers } from 'lucide-react';
import { MaritimeMap } from '../map/MaritimeMap';
import { TimeSlider } from '../dashboard/TimeSlider';

export function DriftView({ incident, candidates, selectedMmsi, onSelectCandidate, visibility, onToggleLayer }) {
  const drift = incident?.drift;

  if (!drift) {
    return (
      <div className="trace-empty-view">
        <Wind size={48} className="empty-icon text-muted" />
        <h2>No Drift Data Available</h2>
        <p>Hydrodynamic drift reconstruction output has not been ingested by the backend server yet.</p>
      </div>
    );
  }

  const originLat = drift.origin_coordinates?.lat != null 
    ? `${Math.abs(drift.origin_coordinates.lat).toFixed(4)}° ${drift.origin_coordinates.lat >= 0 ? 'N' : 'S'}` 
    : 'N/A';
  const originLon = drift.origin_coordinates?.lon != null 
    ? `${Math.abs(drift.origin_coordinates.lon).toFixed(4)}° ${drift.origin_coordinates.lon >= 0 ? 'E' : 'W'}` 
    : 'N/A';

  const startTime = drift.source_time_window?.start_time 
    ? new Date(drift.source_time_window.start_time).toUTCString().slice(17, 22) 
    : 'N/A';
  const endTime = drift.source_time_window?.end_time 
    ? new Date(drift.source_time_window.end_time).toUTCString().slice(17, 22) 
    : 'N/A';

  const uncertainty = drift.uncertainty_radius_km != null ? `${drift.uncertainty_radius_km} km` : 'Data unavailable';

  const backwardPoints = drift.backward_track || [];
  const forecastTracks = drift.forecast_tracks || [];

  return (
    <div className="view-container drift-view-container">
      <div className="view-header">
        <div className="view-title-group">
          <Wind size={22} className="view-icon text-primary" />
          <div>
            <h2 className="view-title">DRIFT ANALYSIS & SOURCE RECONSTRUCTION</h2>
            <span className="view-subtitle">Backward Hindcast Ocean Model & Forward Drift Forecasting</span>
          </div>
        </div>
      </div>

      <div className="view-grid-top">
        <div className="map-column">
          <MaritimeMap 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={onSelectCandidate}
            visibility={visibility}
            onToggleLayer={onToggleLayer}
          />
          <TimeSlider />
        </div>

        <div className="details-column">
          <div className="drift-metrics-card">
            <h3 className="card-section-title"><Target size={16} /> Estimated Origin Region</h3>
            <div className="loc-row">
              <span>Origin Coordinates:</span>
              <strong>{originLat}, {originLon}</strong>
            </div>
            <div className="loc-row">
              <span>Estimated Source Window:</span>
              <strong>{startTime} - {endTime} UTC</strong>
            </div>
            <div className="loc-row">
              <span>Uncertainty Radius:</span>
              <strong className="text-highlight">{uncertainty}</strong>
            </div>
          </div>

          <div className="trajectory-summary-card">
            <h3 className="card-section-title"><Navigation size={16} /> Trajectory Statistics</h3>
            <div className="stat-row">
              <span>Backward Hindcast Track:</span>
              <strong>{backwardPoints.length} waypoints</strong>
            </div>
            <div className="stat-row">
              <span>Forward Forecast Trajectories:</span>
              <strong>{forecastTracks.length} forecast tracks</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Backward Drift Waypoints Table */}
      <div className="view-grid-bottom">
        <div className="waypoints-card">
          <h3 className="card-section-title"><Compass size={16} /> Backward Hindcast Waypoints</h3>
          {backwardPoints.length > 0 ? (
            <div className="table-responsive">
              <table className="trace-vessel-table">
                <thead>
                  <tr>
                    <th>Waypoint #</th>
                    <th>Timestamp</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                  </tr>
                </thead>
                <tbody>
                  {backwardPoints.map((pt, idx) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>{new Date(pt.timestamp).toUTCString().slice(0, 22)}</td>
                      <td>{pt.lat.toFixed(4)}° N</td>
                      <td>{pt.lon.toFixed(4)}° E</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted">No backward drift track points recorded.</p>
          )}
        </div>
      </div>
    </div>
  );
}
