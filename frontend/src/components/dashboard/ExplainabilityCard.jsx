import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, Satellite, Map, Wind, Ship, Award } from 'lucide-react';

export function ExplainabilityCard() {
  const [expanded, setExpanded] = useState(false);

  const stages = [
    {
      title: 'SATELLITE OBSERVATION',
      desc: 'Sentinel-1 SAR radar imagery detects low-backscatter oil anomaly.',
      icon: Satellite,
    },
    {
      title: 'GEOSPATIAL MAPPING',
      desc: 'Segmentation mask processed into georeferenced polygon & centroid.',
      icon: Map,
    },
    {
      title: 'OCEAN DRIFT INFERENCE',
      desc: 'Wind & ocean current model reconstructs backward origin trajectory.',
      icon: Wind,
    },
    {
      title: 'AIS TRAJECTORY CORRELATION',
      desc: 'Historical vessel positions queried within spatial-temporal window.',
      icon: Ship,
    },
    {
      title: 'EXPLAINABLE ATTRIBUTION',
      desc: 'Multi-factor compatibility score computed with explicit evidence audit.',
      icon: Award,
    },
  ];

  return (
    <div className="explainability-card">
      <div className="explain-header" onClick={() => setExpanded(!expanded)}>
        <div className="title-group">
          <HelpCircle size={16} className="explain-icon" />
          <span className="explain-title">HOW DID TRACE REACH THIS RESULT?</span>
        </div>
        <button className="expand-btn">
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      <div className="pipeline-flow-mini">
        {stages.map((st, i) => {
          const Icon = st.icon;
          return (
            <React.Fragment key={st.title}>
              <div className="flow-step" title={st.desc}>
                <Icon size={13} className="flow-step-icon" />
                <span className="flow-step-name">{st.title.split(' ')[0]}</span>
              </div>
              {i < stages.length - 1 && <span className="flow-arrow">→</span>}
            </React.Fragment>
          );
        })}
      </div>

      {expanded && (
        <div className="explain-details-panel">
          <p className="explain-intro">
            TRACE fuses satellite radar sensing, hydrodynamic drift models, and AIS trajectory history to establish explainable source compatibility without black-box inference.
          </p>
          <div className="stages-list">
            {stages.map((st, idx) => {
              const Icon = st.icon;
              return (
                <div key={st.title} className="stage-item">
                  <div className="stage-num">{idx + 1}</div>
                  <div className="stage-content">
                    <div className="stage-head">
                      <Icon size={14} className="stage-icon" />
                      <span className="stage-title">{st.title}</span>
                    </div>
                    <p className="stage-desc">{st.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
