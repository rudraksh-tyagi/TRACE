import { Wind, Target, Clock, Compass, Navigation } from 'lucide-react';

export function DriftSummaryCard({ drift }) {
  const originLat = drift?.origin_coordinates?.lat != null ? `${Math.abs(drift.origin_coordinates.lat).toFixed(2)}° ${drift.origin_coordinates.lat >= 0 ? 'N' : 'S'}` : null;
  const originLon = drift?.origin_coordinates?.lon != null ? `${Math.abs(drift.origin_coordinates.lon).toFixed(2)}° ${drift.origin_coordinates.lon >= 0 ? 'E' : 'W'}` : null;
  const originStr = (originLat && originLon) ? `${originLat}, ${originLon}` : 'Data unavailable';
  
  const startTime = drift?.source_time_window?.start_time 
    ? new Date(drift.source_time_window.start_time).toUTCString().slice(17, 22) 
    : null;
  const endTime = drift?.source_time_window?.end_time 
    ? new Date(drift.source_time_window.end_time).toUTCString().slice(17, 22) 
    : null;
  const timeWindowStr = (startTime && endTime) ? `${startTime} - ${endTime} UTC` : 'Data unavailable';

  const uncertainty = drift?.uncertainty_radius_km != null ? `${drift.uncertainty_radius_km} km` : 'Data unavailable';
  const backwardCount = drift?.backward_track ? `${drift.backward_track.length} waypoints` : 'Data unavailable';
  const forecastCount = drift?.forecast_tracks?.length ? `${drift.forecast_tracks.length} tracks` : 'Data unavailable';

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
          <span className="detail-value">{originStr}</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Clock size={14} className="detail-icon" />
            <span>Source Time Window</span>
          </div>
          <span className="detail-value">{timeWindowStr}</span>
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
            <span>Backward Track</span>
          </div>
          <span className="detail-value">{backwardCount}</span>
        </div>

        <div className="drift-detail-row">
          <div className="detail-label-group">
            <Wind size={14} className="detail-icon text-info" />
            <span>Forward Forecast</span>
          </div>
          <span className="detail-value text-info font-medium">{forecastCount}</span>
        </div>
      </div>
    </div>
  );
}
