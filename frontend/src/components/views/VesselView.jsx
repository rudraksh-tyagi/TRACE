import React from 'react';
import { Ship, Navigation, Gauge, Clock, AlertTriangle, ChevronRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { MaritimeMap } from '../map/MaritimeMap';
import { VesselTable } from '../vessels/VesselTable';
import { VesselSpotlightCard } from '../vessels/VesselSpotlightCard';

export function VesselView({ incident, candidates, selectedMmsi, onSelectCandidate, selectedCandidate, visibility, onToggleLayer }) {
  if (!candidates || candidates.length === 0) {
    return (
      <div className="trace-empty-view">
        <Ship size={48} className="empty-icon text-muted" />
        <h2>No Candidate Vessels Available</h2>
        <p>AIS candidate vessel analysis has not been ingested by the backend server yet.</p>
      </div>
    );
  }

  const selectedTrajectory = selectedCandidate?.trajectory || [];

  return (
    <div className="view-container vessel-view-container">
      <div className="view-header">
        <div className="view-title-group">
          <Ship size={22} className="view-icon text-accent" />
          <div>
            <h2 className="view-title">AIS CANDIDATE VESSEL ANALYSIS</h2>
            <span className="view-subtitle">Maritime AIS Trajectory Inspection & Spatial-Temporal Proximity</span>
          </div>
        </div>
        <span className="candidate-count">{candidates.length} Vessels Ranked</span>
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
          <VesselSpotlightCard vessel={selectedCandidate} />
        </div>
      </div>

      {/* Vessels Table & Trajectory History */}
      <div className="view-grid-bottom">
        <div className="vessel-table-column">
          <VesselTable 
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={onSelectCandidate}
          />
        </div>

        <div className="trajectory-log-column">
          <div className="trajectory-log-card">
            <h3 className="card-section-title"><Navigation size={16} /> Selected Vessel Trajectory Log</h3>
            {selectedTrajectory.length > 0 ? (
              <div className="table-responsive">
                <table className="trace-vessel-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Timestamp</th>
                      <th>Latitude</th>
                      <th>Longitude</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedTrajectory.map((pt, i) => (
                      <tr key={i}>
                        <td>{i + 1}</td>
                        <td>{new Date(pt.timestamp).toUTCString().slice(0, 22)}</td>
                        <td>{pt.lat.toFixed(4)}° N</td>
                        <td>{pt.lon.toFixed(4)}° E</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted">No AIS trajectory points recorded for {selectedCandidate?.vessel_name || 'selected vessel'}.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
