import { Satellite, Image, Layers, ArrowRight } from 'lucide-react';

export function SatelliteEvidence({ spill }) {
  const spillId = spill?.spill_id ? `Spill: ${spill.spill_id}` : 'Sentinel-1 SAR Data';
  const confidenceStr = spill?.confidence != null ? `${(spill.confidence * 100).toFixed(0)}% Confidence` : 'Threshold Detection';
  const areaStr = spill?.area_km2 != null ? `${spill.area_km2} km² geometry` : 'GeoJSON Geometry';

  return (
    <div className="satellite-evidence-card">
      <div className="section-header">
        <Satellite size={16} className="section-icon" />
        <h3 className="section-title">SATELLITE OBSERVATION EVIDENCE</h3>
      </div>

      <div className="sar-pipeline-flow">
        <div className="sar-card">
          <div className="sar-badge">1. SENTINEL-1 SAR</div>
          <div className="sar-preview sar-raw">
            <Image size={24} className="sar-icon" />
            <span>Raw C-Band SAR</span>
          </div>
          <div className="sar-meta">{spillId}</div>
        </div>

        <ArrowRight size={16} className="flow-arrow-icon" />

        <div className="sar-card">
          <div className="sar-badge">2. THRESHOLD DETECT</div>
          <div className="sar-preview sar-threshold">
            <Layers size={24} className="sar-icon" />
            <span>-28.0 dB Backscatter</span>
          </div>
          <div className="sar-meta">{confidenceStr}</div>
        </div>

        <ArrowRight size={16} className="flow-arrow-icon" />

        <div className="sar-card">
          <div className="sar-badge">3. GIS POLYGON</div>
          <div className="sar-preview sar-geometry">
            <div className="spill-polygon-icon"></div>
            <span>Oil Mask GeoJSON</span>
          </div>
          <div className="sar-meta">{areaStr}</div>
        </div>
      </div>
    </div>
  );
}
