import React from 'react';
import { Anchor } from 'lucide-react';

export function LoadingSkeleton() {
  return (
    <div className="trace-loading-container">
      <div className="loading-card">
        <Anchor size={40} className="loading-logo spin-slow" />
        <h3 className="loading-title">TRACE MARINE INTELLIGENCE</h3>
        <p className="loading-desc">Initializing situational map & candidate attribution pipeline...</p>
        <div className="loading-progress-bar">
          <div className="loading-fill"></div>
        </div>
      </div>
    </div>
  );
}
