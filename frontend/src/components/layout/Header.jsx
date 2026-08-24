import React from 'react';
import { 
  Anchor, 
  RefreshCw, 
  Sun, 
  Moon, 
  Copy, 
  Check,
  Play
} from 'lucide-react';

function formatToIST(dateString) {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';

    const formatter = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });

    const parts = formatter.formatToParts(date);
    const getPart = (type) => parts.find(p => p.type === type)?.value || '';

    const day = getPart('day');
    const month = getPart('month');
    const year = getPart('year');
    const hour = getPart('hour');
    const minute = getPart('minute');
    const second = getPart('second');

    return `${day} ${month} ${year} ${hour}:${minute}:${second} (IST)`;
  } catch {
    return 'N/A';
  }
}

export function Header({ health, incidentId, lastUpdated, onRefresh, onRunPipeline, theme, onToggleTheme, loading }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopyId = () => {
    if (incidentId) {
      navigator.clipboard.writeText(incidentId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formattedDate = formatToIST(lastUpdated);

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
        {/* System Connection Status */}
        <div className={`status-pill ${health?.online ? (health?.mockMode ? 'warning' : 'online') : 'offline'}`}>
          <span className="status-dot"></span>
          <div className="status-text">
            <span className="status-title">
              {health?.online ? (health?.mockMode ? 'DEMO MODE' : 'SYSTEM ONLINE') : 'BACKEND OFFLINE'}
            </span>
            <span className="status-desc">
              {health?.online ? (health?.mockMode ? 'Mock Data Active' : 'FastAPI Connected') : 'Backend Unreachable'}
            </span>
          </div>
        </div>

        {/* Incident ID */}
        <div className="incident-id-box">
          <span className="id-label">INCIDENT ID</span>
          <div className="id-value-group">
            <span className="id-value">{incidentId || 'N/A'}</span>
            {incidentId && (
              <button className="copy-btn" onClick={handleCopyId} title="Copy Incident ID">
                {copied ? <Check size={13} className="text-success" /> : <Copy size={13} />}
              </button>
            )}
          </div>
        </div>

        {/* Last Updated */}
        <div className="last-updated-box">
          <span className="updated-label">LAST UPDATED</span>
          <span className="updated-value">{formattedDate}</span>
        </div>

        {/* Run Pipeline Action */}
        <button 
          className={`run-pipeline-btn ${loading ? 'loading' : ''}`} 
          onClick={onRunPipeline}
          disabled={loading}
          title="Run TRACE Pipeline Analysis"
        >
          <Play size={14} className={loading ? 'spin' : ''} />
          <span>Run Pipeline</span>
        </button>

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
