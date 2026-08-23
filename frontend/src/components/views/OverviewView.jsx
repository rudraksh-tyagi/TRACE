import React from 'react';
import { MaritimeMap } from '../map/MaritimeMap';
import { SpillIntelligenceCards } from '../dashboard/SpillIntelligenceCards';
import { DriftSummaryCard } from '../dashboard/DriftSummaryCard';
import { PipelineProgress } from '../dashboard/PipelineProgress';
import { ExplainabilityCard } from '../dashboard/ExplainabilityCard';
import { TimeSlider } from '../dashboard/TimeSlider';
import { VesselTable } from '../vessels/VesselTable';
import { VesselSpotlightCard } from '../vessels/VesselSpotlightCard';
import { AttributionPanel } from '../attribution/AttributionPanel';
import { EvidencePanel } from '../attribution/EvidencePanel';
import { SatelliteEvidence } from '../attribution/SatelliteEvidence';

export function OverviewView({ 
  incident, 
  candidates, 
  selectedMmsi, 
  onSelectCandidate, 
  selectedCandidate, 
  visibility, 
  onToggleLayer 
}) {
  return (
    <>
      {/* Top Pipeline Flow Indicator */}
      <PipelineProgress />

      {/* Top Main Section: Leaflet Map + Right Spill/Drift Intelligence */}
      <div className="dashboard-top-grid">
        <MaritimeMap 
          incident={incident}
          candidates={candidates}
          selectedMmsi={selectedMmsi}
          onSelectCandidate={onSelectCandidate}
          visibility={visibility}
          onToggleLayer={onToggleLayer}
        />

        <div className="dashboard-right-panel">
          <SpillIntelligenceCards spill={incident?.spill} />
          <DriftSummaryCard drift={incident?.drift} />
        </div>
      </div>

      {/* Time Slider for Drift Hindcast / Forecast Timeline */}
      <TimeSlider />

      {/* Bottom Main Section: Ranked Candidates Table + Selected Vessel Attribution & Evidence */}
      <div className="dashboard-bottom-grid">
        <div className="vessel-table-column">
          <VesselTable 
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={onSelectCandidate}
          />
        </div>

        <div className="attribution-evidence-column">
          <VesselSpotlightCard vessel={selectedCandidate} />
          <AttributionPanel candidate={selectedCandidate} />
          <EvidencePanel candidate={selectedCandidate} />
        </div>
      </div>

      {/* Lower Explainability & Satellite Observation Bridge */}
      <SatelliteEvidence spill={incident?.spill} />
      <ExplainabilityCard />
    </>
  );
}
