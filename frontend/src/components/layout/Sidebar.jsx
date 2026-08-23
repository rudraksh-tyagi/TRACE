import React from 'react';
import { 
  LayoutDashboard, 
  Droplet, 
  Wind, 
  Ship, 
  Target, 
  FileText,
  Server,
  Activity
} from 'lucide-react';

export function Sidebar({ activeTab, setActiveTab, health }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'spill', label: 'Spill Intelligence', icon: Droplet },
    { id: 'drift', label: 'Drift Analysis', icon: Wind },
    { id: 'vessels', label: 'Vessel Analysis', icon: Ship },
    { id: 'attribution', label: 'Attribution', icon: Target },
    { id: 'evidence', label: 'Evidence', icon: FileText },
  ];

  return (
    <aside className="trace-sidebar">
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="system-widget">
          <div className="widget-header">
            <Server size={14} className="widget-icon" />
            <span className="widget-title">SYSTEM STATUS</span>
          </div>
          <div className="widget-body">
            <div className="status-row">
              <span className={`status-indicator ${health.online ? 'active' : 'inactive'}`}></span>
              <span className="status-label">
                {health.online ? 'Backend Connected' : 'Backend Offline'}
              </span>
            </div>
            <div className="status-row">
              <Activity size={12} className="meta-icon" />
              <span className="status-meta">API Mode: Demo (Mock Data)</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
