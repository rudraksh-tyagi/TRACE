import React from 'react';
import { Check } from 'lucide-react';

export function PipelineProgress({ incident }) {
  const isDetected = Boolean(incident?.spill?.detected);
  const isMapped = Boolean(incident?.spill?.polygon_geojson);
  const isSourceEstimated = Boolean(incident?.drift?.origin_coordinates);
  const isVesselsAnalyzed = Array.isArray(incident?.ranked_candidates) && incident.ranked_candidates.length > 0;
  const isAttributed = Boolean(incident?.metadata?.generation_timestamp);

  const steps = [
    { num: 1, label: 'DETECTED', done: isDetected },
    { num: 2, label: 'MAPPED', done: isMapped },
    { num: 3, label: 'SOURCE ESTIMATED', done: isSourceEstimated },
    { num: 4, label: 'VESSELS ANALYZED', done: isVesselsAnalyzed },
    { num: 5, label: 'ATTRIBUTION', done: isAttributed },
  ];

  return (
    <div className="pipeline-progress-bar">
      <span className="pipeline-title">INVESTIGATION PIPELINE:</span>
      <div className="pipeline-steps">
        {steps.map((step, idx) => (
          <React.Fragment key={step.num}>
            <div className={`pipeline-step ${step.done ? 'done' : ''}`}>
              <div className="step-bubble">
                {step.done ? <Check size={11} /> : step.num}
              </div>
              <span className="step-label">{step.label}</span>
            </div>
            {idx < steps.length - 1 && <div className="step-connector"></div>}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
