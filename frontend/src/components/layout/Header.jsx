import React from 'react';
import { 
  Anchor, 
  Activity, 
  Database, 
  RefreshCw, 
  Sun, 
  Moon, 
  Copy, 
  Check 
} from 'lucide-react';

export function Header({ health, incidentId, lastUpdated, onRefresh, theme, onToggleTheme, loading }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopyId = () => {
    if (incidentId) {
      navigator.clipboard.writeText(incidentId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formattedDate = lastUpdated 
    ? new Date(lastUpdated).toUTCString().replace('GMT', '(UTC)').replace(/^[^,]+,\s*/, '')
    : '22 May 2025, 10:45 AM (UTC)';

  return (
    <header className="trace-header">
      <div className="header-left">
        <div className="trace-logo">
          <Anchor className="logo-icon" size={24} />
          <div className="logo-text">
            <span className="brand-name">TRACE</span>
            <span className="brand-sub">Marine Oil Spill Intelligence System</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        {/* System Online Status */}
        <div className={`status-pill ${health.online ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <div className="status-text">
            <span className="status-title">
              {health.online ? 'SYSTEM ONLINE' : 'BACKEND OFFLINE'}
            </span>
            <span className="status-desc">
              {health.online ? 'All Systems Operational' : 'Using Local Fallback'}
            </span>
          </div>
        </div>

        {/* Demo Mode Badge */}
        <div className="demo-badge">
          <Database size={14} className="demo-icon" />
          <div className="demo-text">
            <span className="demo-title">DEMO MODE</span>
            <span className="demo-desc">Using Mock Data</span>
          </div>
        </div>

        {/* Incident ID */}
        <div className="incident-id-box">
          <span className="id-label">INCIDENT ID</span>
          <div className="id-value-group">
            <span className="id-value">{incidentId || 'TRC-001'}</span>
            <button className="copy-btn" onClick={handleCopyId} title="Copy Incident ID">
              {copied ? <Check size={13} className="text-success" /> : <Copy size={13} />}
            </button>
          </div>
        </div>

        {/* Last Updated */}
        <div className="last-updated-box">
          <span className="updated-label">LAST UPDATED</span>
          <span className="updated-value">{formattedDate}</span>
        </div>

        {/* Refresh Action */}
        <button 
          className={`refresh-btn ${loading ? 'loading' : ''}`} 
          onClick={onRefresh}
          disabled={loading}
          title="Refresh Intelligence Data"
        >
          <RefreshCw size={15} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>

        {/* Theme Toggle */}
        <button 
          className="theme-toggle-btn" 
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
        </button>
      </div>
    </header>
  );
}
