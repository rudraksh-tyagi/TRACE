import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export function ErrorState({ error, onRetry }) {
  return (
    <div className="trace-error-container">
      <div className="error-card">
        <AlertOctagon size={48} className="error-icon" />
        <h2 className="error-title">BACKEND UNAVAILABLE</h2>
        <p className="error-message">
          {error || 'Unable to load TRACE intelligence data. Make sure backend server is running.'}
        </p>
        <button className="error-retry-btn" onClick={onRetry}>
          <RefreshCw size={16} />
          <span>Retry Connection</span>
        </button>
      </div>
    </div>
  );
}
