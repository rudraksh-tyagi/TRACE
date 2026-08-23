import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export function ErrorState({ error, onRetry }) {
  return (
    <div className="trace-error-container">
      <div className="error-card">
        <AlertOctagon size={48} className="error-icon text-danger" />
        <h2 className="error-title">BACKEND OFFLINE</h2>
        <p className="error-message">
          {error || 'Unable to connect to TRACE backend server. Please verify the FastAPI backend is running.'}
        </p>
        <button className="error-retry-btn" onClick={onRetry}>
          <RefreshCw size={16} />
          <span>Retry Connection</span>
        </button>
      </div>
    </div>
  );
}
