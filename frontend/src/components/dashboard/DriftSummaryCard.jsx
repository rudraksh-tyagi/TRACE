import React from 'react';
import { Wind, Target, Clock, Compass, Navigation } from 'lucide-react';

export function DriftSummaryCard({ drift }) {
  const originLat = drift?.origin_coordinates?.lat ? `${Math.abs(drift.origin_coordinates.lat).toFixed(2)}° N` : '18.32° N';
  const originLon = drift?.origin_coordinates?.lon ? `${Math.abs(drift.origin_coordinates.lon).toFixed(2)}° E` : '72.18° E';
  
  const startTime = drift?.source_time_window?.start_time 
    ? new Date(drift.source_time_window.start_time).toUTCString().slice(17, 22) 
    : '02:00 AM';
  const endTime = drift?.source_time_window?.end_time 
    ? new Date(drift.source_time_window.end_time).toUTCString().slice(17, 22) 
    : '03:30 AM';

  const uncertainty = drift?.uncertainty_radius_km ? `${drift.uncertainty_radius_km} km` : '25.6 km';

  return (
    <div className="drift-summary-section">
      <div className="section-header">
        <Wind size={16} className="section-icon" />
        <h3 className="section-title">DRIFT SUMMARY</h3>
      </div>

      <div className="drift-details-list">
        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Target size={14} className="detail-icon" />
            <span>Probable Source</span>
          </div>
          <span className="detail-value">{originLat}, {originLon}</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Clock size={14} className="detail-icon" />
            <span>Source Time Window</span>
          </div>
          <span className="detail-value">{startTime} - {endTime} UTC</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Compass size={14} className="detail-icon" />
            <span>Uncertainty Radius</span>
          </div>
          <span className="detail-value">{uncertainty}</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Navigation size={14} className="detail-icon" />
            <span>Backward Drift Length</span>
          </div>
          <span className="detail-value">87.3 km</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Wind size={14} className="detail-icon text-info" />
            <span>Forward Forecast</span>
          </div>
          <span className="detail-value text-info font-medium">Available (24h)</span>
        </div>
      </div>
    </div>
  );
}
