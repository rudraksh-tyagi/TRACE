import { AlertTriangle, RefreshCw } from 'lucide-react';

export function StaleDataBanner({ error, onRetry, loading }) {
  if (!error) return null;

  return (
    <div className="trace-stale-banner">
      <div className="banner-content">
        <AlertTriangle size={16} className="banner-icon text-warning" />
        <span className="banner-text">
          <strong>PIPELINE / DATA SYNC WARNING:</strong> {error} (Displaying last valid incident state).
        </span>
      </div>
      <button 
        className="banner-retry-btn" 
        onClick={onRetry} 
        disabled={loading}
        title="Retry backend sync"
      >
        <RefreshCw size={13} className={loading ? 'spin' : ''} />
        <span>Retry Sync</span>
      </button>
    </div>
  );
}
