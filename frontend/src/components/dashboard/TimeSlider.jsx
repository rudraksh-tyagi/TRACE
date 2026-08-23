import React, { useState } from 'react';
import { Clock, Play, Pause } from 'lucide-react';

export function TimeSlider() {
  const [activeStep, setActiveStep] = useState(3); // Default 'NOW'
  const [isPlaying, setIsPlaying] = useState(false);

  const steps = [
    { label: '-12h', desc: 'Hindcast Origin' },
    { label: '-6h', desc: 'Drift Hindcast' },
    { label: '-2h', desc: 'Near Source' },
    { label: 'NOW', desc: 'SAR Detection' },
    { label: '+6h', desc: 'Forecast +6h' },
    { label: '+12h', desc: 'Forecast +12h' },
  ];

  const handlePlayToggle = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="drift-time-slider-box">
      <div className="slider-header">
        <div className="title-group">
          <Clock size={14} className="icon" />
          <span>DRIFT TIMELINE SLIDER</span>
        </div>
        <div className="active-time-readout">
          {steps[activeStep].label} ({steps[activeStep].desc})
        </div>
      </div>

      <div className="slider-controls">
        <button className="play-btn" onClick={handlePlayToggle}>
          {isPlaying ? <Pause size={13} /> : <Play size={13} />}
        </button>

        <div className="ticks-container">
          {steps.map((st, idx) => (
            <button
              key={st.label}
              className={`tick-btn ${idx === activeStep ? 'active' : ''} ${st.label === 'NOW' ? 'now-tick' : ''}`}
              onClick={() => setActiveStep(idx)}
            >
              <span className="tick-dot"></span>
              <span className="tick-label">{st.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
