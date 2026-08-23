import React, { useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { useIncidentData } from './hooks/useIncidentData';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { MaritimeMap } from './components/map/MaritimeMap';
import { SpillIntelligenceCards } from './components/dashboard/SpillIntelligenceCards';
import { DriftSummaryCard } from './components/dashboard/DriftSummaryCard';
import { PipelineProgress } from './components/dashboard/PipelineProgress';
import { ExplainabilityCard } from './components/dashboard/ExplainabilityCard';
import { TimeSlider } from './components/dashboard/TimeSlider';
import { VesselTable } from './components/vessels/VesselTable';
import { VesselSpotlightCard } from './components/vessels/VesselSpotlightCard';
import { AttributionPanel } from './components/attribution/AttributionPanel';
import { EvidencePanel } from './components/attribution/EvidencePanel';
import { SatelliteEvidence } from './components/attribution/SatelliteEvidence';
import { ErrorState } from './components/common/ErrorState';
import { LoadingSkeleton } from './components/common/LoadingSkeleton';

function App() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('overview');

  const {
    loading,
    error,
    health,
    incident,
    candidates,
    selectedMmsi,
    setSelectedMmsi,
    selectedCandidate,
    refreshData,
    layerVisibility,
    toggleLayer,
  } = useIncidentData();

  if (loading && !incident) {
    return <LoadingSkeleton />;
  }

  if (error && !incident) {
    return <ErrorState error={error} onRetry={refreshData} />;
  }

  return (
    <div className="trace-app-root">
      {/* 1. Command Header */}
      <Header 
        health={health}
        incidentId={incident?.incident_id}
        lastUpdated={incident?.metadata?.generation_timestamp}
        onRefresh={refreshData}
        theme={theme}
        onToggleTheme={toggleTheme}
        loading={loading}
      />

      <div className="trace-body-container">
        {/* 2. Left Sidebar Navigation */}
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          health={health} 
        />

        {/* 3. Main Dashboard Canvas */}
        <main className="trace-main-content">
          {/* Top Pipeline Flow Indicator */}
          <PipelineProgress />

          {/* Top Main Section: Leaflet Map + Right Spill/Drift Intelligence */}
          <div className="dashboard-top-grid">
            <MaritimeMap 
              incident={incident}
              candidates={candidates}
              selectedMmsi={selectedMmsi}
              onSelectCandidate={setSelectedMmsi}
              visibility={layerVisibility}
              onToggleLayer={toggleLayer}
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
                onSelectCandidate={setSelectedMmsi}
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
        </main>
      </div>
    </div>
  );
}

export default App;
