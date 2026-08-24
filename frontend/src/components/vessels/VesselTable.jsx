import { Ship, ChevronRight, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

export function VesselTable({ candidates, selectedMmsi, onSelectCandidate }) {
  const getStatusBadge = (score) => {
    if (score >= 80) return { label: 'High', class: 'badge-high' };
    if (score >= 60) return { label: 'Medium', class: 'badge-medium' };
    if (score >= 30) return { label: 'Low', class: 'badge-low' };
    return { label: 'Very Low', class: 'badge-verylow' };
  };

  const getPresenceBadge = (vessel) => {
    if (vessel.source_window_presence === true) {
      return <span className="presence-yes"><CheckCircle2 size={13} /> Yes</span>;
    }
    if (vessel.source_window_presence === false) {
      return <span className="presence-no"><XCircle size={13} /> No</span>;
    }
    if (typeof vessel.time_spent_near_source_min === 'number' && vessel.time_spent_near_source_min > 0) {
      return <span className="presence-partial"><AlertCircle size={13} /> Partial</span>;
    }
    return <span className="presence-unknown text-muted">Unknown</span>;
  };

  return (
    <div className="vessel-table-section">
      <div className="section-header">
        <div className="title-group">
          <Ship size={16} className="section-icon" />
          <h3 className="section-title">CANDIDATE VESSELS</h3>
        </div>
        <span className="candidate-count">{candidates.length} Ranked Candidates</span>
      </div>

      <div className="table-responsive">
        <table className="trace-vessel-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Vessel Name</th>
              <th>MMSI</th>
              <th>Vessel Type</th>
              <th>Min. Distance (km)</th>
              <th>Source Window Presence</th>
              <th>Attribution Score</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((vessel, index) => {
              const isSelected = vessel.mmsi === selectedMmsi;
              const status = getStatusBadge(vessel.overall_score);

              return (
                <tr 
                  key={vessel.mmsi} 
                  className={`vessel-row ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectCandidate(vessel.mmsi)}
                >
                  <td className="rank-col">{index + 1}</td>
                  <td className="vessel-name-col font-medium">
                    <Ship size={14} className="vessel-row-icon" />
                    <span>{vessel.vessel_name}</span>
                  </td>
                  <td className="mmsi-col">{vessel.mmsi}</td>
                  <td className="type-col">{vessel.vessel_type}</td>
                  <td className="dist-col">{typeof vessel.minimum_distance_km === 'number' ? `${vessel.minimum_distance_km} km` : vessel.minimum_distance_km}</td>
                  <td className="presence-col">{getPresenceBadge(vessel)}</td>
                  <td className="score-col font-bold">
                    <span className="score-number">{vessel.overall_score}%</span>
                  </td>
                  <td className="status-col">
                    <span className={`status-pill-sm ${status.class}`}>{status.label}</span>
                  </td>
                  <td className="action-col">
                    <button className="select-row-btn" title="Inspect Vessel">
                      <ChevronRight size={15} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
