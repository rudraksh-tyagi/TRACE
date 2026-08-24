import React from 'react';
import { Droplet, ShieldCheck, Maximize, Clock, MapPin, AlertTriangle, Layers, Satellite, FileText } from 'lucide-react';
import { MaritimeMap } from '../map/MaritimeMap';

export function SpillView({ incident, candidates, selectedMmsi, onSelectCandidate, visibility, onToggleLayer }) {
  const spill = incident?.spill;

  if (!spill) {
    return (
      <div className="trace-empty-view">
        <Droplet size={48} className="empty-icon text-muted" />
        <h2>No Spill Data Available</h2>
        <p>GIS oil spill detection output has not been ingested by the backend server yet.</p>
      </div>
    );
  }

  const area = spill.area_km2 != null ? `${spill.area_km2} km²` : 'Data unavailable';
  const confidence = spill.confidence != null ? `${(spill.confidence * 100).toFixed(0)}%` : 'N/A';
  const perimeter = spill.perimeter_km != null ? `${spill.perimeter_km} km` : 'Data unavailable';
  const timestamp = spill.timestamp 
    ? new Date(spill.timestamp).toUTCString().replace('GMT', '(UTC)').replace(/^[^,]+,\s*/, '')
    : 'Data unavailable';

  const lat = spill.centroid?.lat != null ? `${Math.abs(spill.centroid.lat).toFixed(4)}° ${spill.centroid.lat >= 0 ? 'N' : 'S'}` : 'N/A';
  const lon = spill.centroid?.lon != null ? `${Math.abs(spill.centroid.lon).toFixed(4)}° ${spill.centroid.lon >= 0 ? 'E' : 'W'}` : 'N/A';

  const bbox = spill.bounding_box;

  return (
    <div className="view-container spill-view-container">
      <div className="view-header">
        <div className="view-title-group">
          <Droplet size={22} className="view-icon text-danger" />
          <div>
            <h2 className="view-title">SPILL INTELLIGENCE ANALYSIS</h2>
            <span className="view-subtitle">Sentinel-1 SAR Detection & Georeferenced Polygon Geometry</span>
          </div>
        </div>
        <div className="view-id-badge">
          <span>SPILL ID: <strong>{spill.spill_id || 'N/A'}</strong></span>
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
        </div>

        <div className="details-column">
          <div className="spill-metrics-card">
            <h3 className="card-section-title"><Droplet size={16} /> Key Spatial Metrics</h3>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Spill Area</span>
                <span className="metric-value text-danger">{area}</span>
              </div>

              <div className="metric-item">
                <span className="metric-label">Detection Confidence</span>
                <span className="metric-value text-success">{confidence}</span>
              </div>

              <div className="metric-item">
                <span className="metric-label">Perimeter</span>
                <span className="metric-value">{perimeter}</span>
              </div>

              <div className="metric-item">
                <span className="metric-label">Status</span>
                <span className="metric-value text-success">{spill.detected ? 'DETECTED' : 'CLEAR'}</span>
              </div>
            </div>
          </div>

          <div className="location-card">
            <h3 className="card-section-title"><MapPin size={16} /> Centroid & Coordinates</h3>
            <div className="location-details-list">
              <div className="loc-row">
                <span>Latitude:</span>
                <strong>{lat}</strong>
              </div>
              <div className="loc-row">
                <span>Longitude:</span>
                <strong>{lon}</strong>
              </div>
              <div className="loc-row">
                <span>Acquisition Timestamp:</span>
                <strong>{timestamp}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Extended GIS & Bounding Box Properties */}
      <div className="view-grid-bottom">
        <div className="bbox-card">
          <h3 className="card-section-title"><Maximize size={16} /> Geographic Bounding Box</h3>
          {bbox ? (
            <div className="bbox-grid">
              <div className="bbox-item"><span>Min Lat:</span> <strong>{bbox.min_lat?.toFixed(4)}°</strong></div>
              <div className="bbox-item"><span>Max Lat:</span> <strong>{bbox.max_lat?.toFixed(4)}°</strong></div>
              <div className="bbox-item"><span>Min Lon:</span> <strong>{bbox.min_lon?.toFixed(4)}°</strong></div>
              <div className="bbox-item"><span>Max Lon:</span> <strong>{bbox.max_lon?.toFixed(4)}°</strong></div>
            </div>
          ) : (
            <p className="text-muted">Bounding box coordinates unavailable for current geometry.</p>
          )}
        </div>

        <div className="sensor-card">
          <h3 className="card-section-title"><Satellite size={16} /> Satellite Detection Metadata</h3>
          <div className="sensor-details">
            <div className="sensor-row"><span>Sensor Source:</span> <strong>Sentinel-1 SAR C-Band Radar</strong></div>
            <div className="sensor-row"><span>Detection Method:</span> <strong>Backscatter Threshold (-28.0 dB) + Connected Components</strong></div>
            <div className="sensor-row"><span>Format:</span> <strong>GeoJSON Polygon Geometry</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
}
