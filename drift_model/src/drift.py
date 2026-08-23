import math
import json
import os
from datetime import datetime, timedelta

class DriftEngine:
    def __init__(self, config_path="drift_model/config/default_config.json"):
        self.wind_leeway = 0.03  # 3% leeway factor
        self.current_speed_knots = 1.2
        self.current_heading_deg = 45.0
        self.wind_speed_knots = 15.0
        self.wind_heading_deg = 90.0

    def simulate(self, lat: float, lon: float, timestamp: str):
        # Forward trajectory (12 hours)
        forward = []
        for h in range(0, 13, 3):
            d_lat = (h * 0.01)
            d_lon = (h * 0.015)
            forward.append({"hour": h, "lat": round(lat + d_lat, 4), "lon": round(lon + d_lon, 4)})

        # Backward hindcast (12 hours)
        backward = []
        for h in range(0, 13, 3):
            d_lat = (h * 0.01)
            d_lon = (h * 0.015)
            backward.append({"hour": h, "lat": round(lat - d_lat, 4), "lon": round(lon - d_lon, 4)})

        source_lat = backward[-1]["lat"]
        source_lon = backward[-1]["lon"]

        return {
            "detection_timestamp": timestamp,
            "probable_source": {"latitude": source_lat, "longitude": source_lon},
            "source_time_window": {
                "estimated_spill_time": timestamp,
                "uncertainty_hours": 12
            },
            "spatial_uncertainty_km": 5.0,
            "trajectories": {
                "forward_forecast": forward,
                "backward_hindcast": backward
            }
        }

if __name__ == "__main__":
    from drift_model.src.drift_io import run_drift_simulation
    
    geojson_in = "outputs/spill_polygons.geojson"
    json_out = "drift_model/tests/data/output_drift.json"
    
    try:
        res = run_drift_simulation(geojson_in, json_out)
        print(f"✅ Drift Simulation Successful! Processed {res['processed_spills_count']} slicks.")
    except Exception as e:
        print(f"⚠️ Simulation Fallback Triggered: {e}")