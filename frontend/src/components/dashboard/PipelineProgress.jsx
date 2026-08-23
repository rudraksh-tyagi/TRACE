import React from 'react';
import { Check } from 'lucide-react';

export function PipelineProgress() {
  const steps = [
    { num: 1, label: 'DETECTED', done: true },
    { num: 2, label: 'MAPPED', done: true },
    { num: 3, label: 'SOURCE ESTIMATED', done: true },
    { num: 4, label: 'VESSELS ANALYZED', done: true },
    { num: 5, label: 'ATTRIBUTION', done: true },
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
