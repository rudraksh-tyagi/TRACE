import { useState } from 'react';
import { Layers, X, ChevronDown } from 'lucide-react';

export function LayerControl({ visibility, onToggle }) {
  const [isOpen, setIsOpen] = useState(true);

  const layerItems = [
    { key: 'spillPolygon', label: 'Oil Spill Polygon', color: '#EF4444' },
    { key: 'spillCentroid', label: 'Spill Centroid', color: '#F97316' },
    { key: 'sourceRegion', label: 'Source Region', color: '#10B981' },
    { key: 'uncertaintyRegion', label: 'Uncertainty Region', color: '#059669' },
    { key: 'backwardDrift', label: 'Backward Drift', color: '#8B5CF6' },
    { key: 'forwardForecast', label: 'Forward Forecast', color: '#06B6D4' },
    { key: 'vesselTrajectories', label: 'Vessel Trajectories', color: '#3B82F6' },
  ];

  return (
    <div className={`map-layer-panel ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="panel-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="title-group">
          <Layers size={14} className="panel-icon" />
          <span>MAP LAYERS</span>
        </div>
        <button className="toggle-collapse-btn">
          {isOpen ? <X size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {isOpen && (
        <div className="panel-body">
          {layerItems.map((item) => (
            <label key={item.key} className="layer-checkbox-item">
              <input
                type="checkbox"
                checked={!!visibility[item.key]}
                onChange={() => onToggle(item.key)}
              />
              <span className="custom-checkbox"></span>
              <span className="layer-color-dot" style={{ backgroundColor: item.color }}></span>
              <span className="layer-name">{item.label}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
