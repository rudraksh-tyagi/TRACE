import React, { useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { useIncidentData } from './hooks/useIncidentData';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { ErrorState } from './components/common/ErrorState';
import { LoadingSkeleton } from './components/common/LoadingSkeleton';

import { OverviewView } from './components/views/OverviewView';
import { SpillView } from './components/views/SpillView';
import { DriftView } from './components/views/DriftView';
import { VesselView } from './components/views/VesselView';
import { AttributionView } from './components/views/AttributionView';
import { EvidenceView } from './components/views/EvidenceView';

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
    runPipeline,
    layerVisibility,
    toggleLayer,
  } = useIncidentData();

  if (loading && !incident) {
    return <LoadingSkeleton />;
  }

  if (error && !incident) {
    return <ErrorState error={error} onRetry={refreshData} />;
  }

  const renderActiveView = () => {
    switch (activeTab) {
      case 'spill':
        return (
          <SpillView 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            visibility={layerVisibility}
            onToggleLayer={toggleLayer}
          />
        );
      case 'drift':
        return (
          <DriftView 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            visibility={layerVisibility}
            onToggleLayer={toggleLayer}
          />
        );
      case 'vessels':
        return (
          <VesselView 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            selectedCandidate={selectedCandidate}
            visibility={layerVisibility}
            onToggleLayer={toggleLayer}
          />
        );
      case 'attribution':
        return (
          <AttributionView 
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            selectedCandidate={selectedCandidate}
          />
        );
      case 'evidence':
        return (
          <EvidenceView 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            selectedCandidate={selectedCandidate}
          />
        );
      case 'overview':
      default:
        return (
          <OverviewView 
            incident={incident}
            candidates={candidates}
            selectedMmsi={selectedMmsi}
            onSelectCandidate={setSelectedMmsi}
            selectedCandidate={selectedCandidate}
            visibility={layerVisibility}
            onToggleLayer={toggleLayer}
          />
        );
    }
  };

  return (
    <div className="trace-app-root">
      {/* 1. Command Header */}
      <Header 
        health={health}
        incidentId={incident?.incident_id}
        lastUpdated={incident?.metadata?.generation_timestamp}
        onRefresh={refreshData}
        onRunPipeline={runPipeline}
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
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;

