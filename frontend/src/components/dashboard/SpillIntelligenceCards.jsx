import React from 'react';
import { Droplet, ShieldCheck, Maximize, Clock, MapPin, AlertTriangle } from 'lucide-react';

export function SpillIntelligenceCards({ spill }) {
  const area = spill?.area_km2 ? `${spill.area_km2} km²` : '18.6 km²';
  const confidence = spill?.confidence ? `${(spill.confidence * 100).toFixed(0)}%` : '94%';
  const perimeter = spill?.perimeter_km ? `${spill.perimeter_km} km` : '27.4 km';
  const timestamp = spill?.timestamp 
    ? new Date(spill.timestamp).toUTCString().replace('GMT', '(UTC)').replace(/^[^,]+,\s*/, '')
    : '22 May 2025, 08:15 AM (UTC)';
  
  const lat = spill?.centroid?.lat ? `${Math.abs(spill.centroid.lat).toFixed(2)}° N` : '18.42° N';
  const lon = spill?.centroid?.lon ? `${Math.abs(spill.centroid.lon).toFixed(2)}° E` : '72.81° E';

  return (
    <div className="spill-intelligence-section">
      <div className="section-header">
        <Droplet size={16} className="section-icon" />
        <h3 className="section-title">SPILL INTELLIGENCE</h3>
      </div>

      <div className="metrics-grid">
        {/* Metric 1: Spill Area */}
        <div className="metric-card">
          <div className="card-header">
            <Droplet size={15} className="card-icon text-danger" />
            <span className="card-label">SPILL AREA</span>
          </div>
          <div className="card-value">{area}</div>
          <div className="card-sub">Estimated Area</div>
        </div>

        {/* Metric 2: Confidence */}
        <div className="metric-card">
          <div className="card-header">
            <ShieldCheck size={15} className="card-icon text-success" />
            <span className="card-label">CONFIDENCE</span>
          </div>
          <div className="card-value text-success">{confidence}</div>
          <div className="card-sub">High Confidence</div>
        </div>

        {/* Metric 3: Perimeter */}
        <div className="metric-card">
          <div className="card-header">
            <Maximize size={15} className="card-icon text-primary" />
            <span className="card-label">PERIMETER</span>
          </div>
          <div className="card-value">{perimeter}</div>
          <div className="card-sub">Estimated Perimeter</div>
        </div>

        {/* Metric 4: Status */}
        <div className="metric-card">
          <div className="card-header">
            <AlertTriangle size={15} className="card-icon text-success" />
            <span className="card-label">STATUS</span>
          </div>
          <div className="card-value text-success">DETECTED</div>
          <div className="card-sub">Oil Spill Detected</div>
        </div>

        {/* Metric 5: Detection Time */}
        <div className="metric-card">
          <div className="card-header">
            <Clock size={15} className="card-icon text-info" />
            <span className="card-label">DETECTION TIME</span>
          </div>
          <div className="card-value-sm">{timestamp}</div>
          <div className="card-sub">Sentinel-1 SAR</div>
        </div>

        {/* Metric 6: Location */}
        <div className="metric-card">
          <div className="card-header">
            <MapPin size={15} className="card-icon text-accent" />
            <span className="card-label">LOCATION</span>
          </div>
          <div className="card-value-sm">{lat} {lon}</div>
          <div className="card-sub">Arabian Sea</div>
        </div>
      </div>
    </div>
  );
}
