import React, { useEffect, useMemo } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  GeoJSON, 
  Marker, 
  Popup, 
  Circle, 
  Polyline, 
  Tooltip,
  useMap 
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LayerControl } from './LayerControl';
import { Maximize2, Compass } from 'lucide-react';

// Fix default leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Icon Creators
function createCustomMarkerIcon(color, label, isSelected = false) {
  const size = isSelected ? 34 : 26;
  return L.divIcon({
    className: 'custom-map-icon',
    html: `
      <div style="
        background-color: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid ${isSelected ? '#FFFFFF' : 'rgba(255,255,255,0.7)'};
        box-shadow: 0 0 ${isSelected ? '12px' : '4px'} ${color};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 11px;
        cursor: pointer;
      ">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M2 21L12 3l10 18-10-4z"/>
        </svg>
      </div>
      ${label ? `<div class="marker-label ${isSelected ? 'selected' : ''}">${label}</div>` : ''}
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

function createSourceIcon() {
  return L.divIcon({
    className: 'source-map-icon',
    html: `
      <div style="
        background: #10B981;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        box-shadow: 0 0 10px #10B981;
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="background: white; width: 6px; height: 6px; border-radius: 50%;"></div>
      </div>
    `,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
}

function createCentroidIcon() {
  return L.divIcon({
    className: 'centroid-map-icon',
    html: `
      <div style="
        background: #F97316;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        box-shadow: 0 0 8px #F97316;
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="background: white; width: 6px; height: 6px; border-radius: 50%;"></div>
      </div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

// Controller component to handle map bounds pan/zoom
function MapBoundsController({ bbox, centroid }) {
  const map = useMap();

  useEffect(() => {
    if (bbox) {
      const bounds = L.latLngBounds(
        [bbox.min_lat, bbox.min_lon],
        [bbox.max_lat, bbox.max_lon]
      );
      map.fitBounds(bounds, { padding: [80, 80], maxZoom: 12 });
    } else if (centroid) {
      map.setView([centroid.lat, centroid.lon], 10);
    }
  }, [map, bbox, centroid]);

  return null;
}

export function MaritimeMap({ 
  incident, 
  candidates, 
  selectedMmsi, 
  onSelectCandidate,
  visibility,
  onToggleLayer 
}) {
  const spill = incident?.spill;
  const drift = incident?.drift;

  const defaultCenter = useMemo(() => {
    if (spill?.centroid) {
      return [spill.centroid.lat, spill.centroid.lon];
    }
    return [18.4200, 72.8100];
  }, [spill]);

  // Backward drift coordinates array for polyline
  const backwardPolyline = useMemo(() => {
    if (!drift?.backward_track) return [];
    return drift.backward_track.map(pt => [pt.lat, pt.lon]);
  }, [drift]);

  // Forward forecast coordinates
  const forecastPolylines = useMemo(() => {
    if (!drift?.forecast_tracks) return [];
    return drift.forecast_tracks.map(tr => tr.points.map(pt => [pt.lat, pt.lon]));
  }, [drift]);

  return (
    <div className="maritime-map-wrapper">
      <div className="map-title-bar">
        <span className="map-title">MARITIME SITUATIONAL MAP</span>
        <div className="map-coords-badge">
          <Compass size={13} />
          <span>
            {spill?.centroid 
              ? `${Math.abs(spill.centroid.lat).toFixed(2)}° N, ${Math.abs(spill.centroid.lon).toFixed(2)}° E` 
              : '18.42° N, 72.81° E'}
          </span>
        </div>
      </div>

      <MapContainer 
        center={defaultCenter} 
        zoom={9} 
        scrollWheelZoom={true}
        className="leaflet-container-custom"
      >
        {/* Bounds controller */}
        {spill && <MapBoundsController bbox={spill.bounding_box} centroid={spill.centroid} />}

        {/* Satellite Map Tile Layer (Esri World Imagery or CartoDB Voyager) */}
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={18}
        />

        {/* Layer Controls Panel */}
        <LayerControl visibility={visibility} onToggle={onToggleLayer} />

        {/* 1. Oil Spill Polygon */}
        {visibility.spillPolygon && spill?.polygon_geojson && (
          <GeoJSON
            key={spill.spill_id || 'spill-geojson'}
            data={spill.polygon_geojson}
            style={{
              color: '#EF4444',
              weight: 2.5,
              opacity: 0.9,
              fillColor: '#DC2626',
              fillOpacity: 0.45,
              dashArray: '4, 4'
            }}
          >
            <Tooltip permanent direction="top" className="spill-tooltip">
              OIL SPILL DETECTED<br/>
              <small>{new Date(spill.timestamp).toUTCString().slice(0, 22)}</small>
            </Tooltip>
          </GeoJSON>
        )}

        {/* 2. Spill Centroid */}
        {visibility.spillCentroid && spill?.centroid && (
          <Marker 
            position={[spill.centroid.lat, spill.centroid.lon]}
            icon={createCentroidIcon()}
          >
            <Popup className="trace-popup">
              <div className="popup-content">
                <h4>SPILL CENTROID</h4>
                <p><strong>Lat/Lon:</strong> {spill.centroid.lat.toFixed(4)}, {spill.centroid.lon.toFixed(4)}</p>
                <p><strong>Area:</strong> {spill.area_km2} km²</p>
                <p><strong>Confidence:</strong> {(spill.confidence * 100).toFixed(0)}%</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* 3. Source Region & Uncertainty Circle */}
        {visibility.sourceRegion && drift?.origin_coordinates && (
          <>
            <Marker 
              position={[drift.origin_coordinates.lat, drift.origin_coordinates.lon]}
              icon={createSourceIcon()}
            >
              <Popup className="trace-popup">
                <div className="popup-content">
                  <h4>PROBABLE SOURCE REGION</h4>
                  <p><strong>Origin:</strong> {drift.origin_coordinates.lat.toFixed(4)}, {drift.origin_coordinates.lon.toFixed(4)}</p>
                  <p><strong>Window:</strong> {new Date(drift.source_time_window.start_time).toUTCString().slice(17, 22)} - {new Date(drift.source_time_window.end_time).toUTCString().slice(17, 22)} UTC</p>
                </div>
              </Popup>
              <Tooltip permanent direction="bottom" className="source-tooltip">
                PROBABLE SOURCE<br/>
                <small>{new Date(drift.source_time_window.start_time).toUTCString().slice(0, 22)}</small>
              </Tooltip>
            </Marker>

            {visibility.uncertaintyRegion && (
              <Circle
                center={[drift.origin_coordinates.lat, drift.origin_coordinates.lon]}
                radius={(drift.uncertainty_radius_km || 15) * 1000}
                pathOptions={{
                  color: '#10B981',
                  weight: 1.5,
                  dashArray: '6, 6',
                  fillColor: '#10B981',
                  fillOpacity: 0.12
                }}
              />
            )}
          </>
        )}

        {/* 4. Backward Drift Hindcast Track */}
        {visibility.backwardDrift && backwardPolyline.length > 0 && (
          <Polyline
            positions={backwardPolyline}
            pathOptions={{
              color: '#8B5CF6',
              weight: 3,
              dashArray: '8, 8',
              opacity: 0.85
            }}
          >
            <Tooltip sticky>Backward Hindcast Drift Vector</Tooltip>
          </Polyline>
        )}

        {/* 5. Forward Forecast Tracks */}
        {visibility.forwardForecast && forecastPolylines.map((track, i) => (
          <Polyline
            key={`forecast-${i}`}
            positions={track}
            pathOptions={{
              color: '#06B6D4',
              weight: 2.5,
              dashArray: '4, 4',
              opacity: 0.8
            }}
          >
            <Tooltip sticky>Forward Drift Forecast Track</Tooltip>
          </Polyline>
        ))}

        {/* 6. Candidate Vessel Trajectories & Markers */}
        {candidates.map((vessel) => {
          const isSelected = vessel.mmsi === selectedMmsi;
          const trajectoryPoints = vessel.trajectory?.map(pt => [pt.lat, pt.lon]) || [];
          const lastPoint = trajectoryPoints.length > 0 
            ? trajectoryPoints[trajectoryPoints.length - 1] 
            : [18.4 + Math.random() * 0.2, 72.8 + Math.random() * 0.2];

          const color = isSelected ? '#F59E0B' : (vessel.overall_score >= 80 ? '#3B82F6' : '#64748B');

          return (
            <React.Fragment key={vessel.mmsi}>
              {/* Vessel Trajectory Polyline */}
              {visibility.vesselTrajectories && trajectoryPoints.length > 0 && (
                <Polyline
                  positions={trajectoryPoints}
                  pathOptions={{
                    color: color,
                    weight: isSelected ? 4 : 2,
                    opacity: isSelected ? 0.95 : 0.6,
                  }}
                />
              )}

              {/* Vessel Position Marker */}
              <Marker
                position={lastPoint}
                icon={createCustomMarkerIcon(color, `${vessel.vessel_name} (${vessel.vessel_type})`, isSelected)}
                eventHandlers={{
                  click: () => onSelectCandidate(vessel.mmsi),
                }}
              >
                <Popup className="trace-popup">
                  <div className="popup-content">
                    <h4>{vessel.vessel_name}</h4>
                    <p><strong>MMSI:</strong> {vessel.mmsi}</p>
                    <p><strong>Type:</strong> {vessel.vessel_type}</p>
                    <p><strong>Min Distance:</strong> {vessel.minimum_distance_km} km</p>
                    <p><strong>Compatibility Score:</strong> <span className="text-highlight">{vessel.overall_score}%</span></p>
                    <button 
                      className="popup-select-btn" 
                      onClick={() => onSelectCandidate(vessel.mmsi)}
                    >
                      Inspect Vessel Attribution
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}
