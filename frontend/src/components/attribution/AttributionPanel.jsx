import React from 'react';
import { Target, Award } from 'lucide-react';

export function AttributionPanel({ candidate }) {
  if (!candidate) return null;

  const score = candidate.overall_score || 0;
  const comp = candidate.component_scores || {
    distance_score: 0,
    time_compatibility_score: 0,
    trajectory_consistency_score: 0,
    behavior_score: 0,
  };

  const vesselName = candidate.vessel_name || candidate.vessel_identity || `Vessel ${candidate.mmsi}`;

  // SVG Donut calculation
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="attribution-details-section">
      <div className="section-header">
        <Target size={16} className="section-icon" />
        <h3 className="section-title">
          ATTRIBUTION DETAILS – <span className="vessel-highlight">{vesselName}</span>
        </h3>
      </div>

      <div className="attribution-content-grid">
        {/* Left Donut Gauge */}
        <div className="score-donut-box">
          <span className="box-label">OVERALL SOURCE COMPATIBILITY SCORE</span>
          <div className="donut-wrapper">
            <svg width="120" height="120" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="donut-bg"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="donut-progress"
                style={{
                  strokeDasharray: circumference,
                  strokeDashoffset: strokeDashoffset,
                }}
              />
            </svg>
            <div className="donut-center-text">
              <span className="donut-number">{score}%</span>
              <span className="donut-sub">High Confidence</span>
            </div>
          </div>
        </div>

        {/* Right Progress Bars */}
        <div className="component-scores-box">
          <span className="box-label">COMPONENT SCORES</span>

          <div className="score-bar-group">
            <div className="bar-header">
              <span className="bar-title">Distance Score</span>
              <span className="bar-val">{comp.distance_score}%</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-green" 
                style={{ width: `${comp.distance_score}%` }}
              ></div>
            </div>
          </div>

          <div className="score-bar-group">
            <div className="bar-header">
              <span className="bar-title">Time Compatibility</span>
              <span className="bar-val">{comp.time_compatibility_score}%</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-green" 
                style={{ width: `${comp.time_compatibility_score}%` }}
              ></div>
            </div>
          </div>

          <div className="score-bar-group">
            <div className="bar-header">
              <span className="bar-title">Trajectory Consistency</span>
              <span className="bar-val">{comp.trajectory_consistency_score}%</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-green" 
                style={{ width: `${comp.trajectory_consistency_score}%` }}
              ></div>
            </div>
          </div>

          <div className="score-bar-group">
            <div className="bar-header">
              <span className="bar-title">Behavior Score</span>
              <span className="bar-val">{comp.behavior_score}%</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-cyan" 
                style={{ width: `${comp.behavior_score}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
