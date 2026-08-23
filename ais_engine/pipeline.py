import json
import math
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the earth in km.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def parse_drift_input(drift_data):
    """
    Extract source center coordinates, time window, and radius from flexible drift formats.
    """
    # Check for multi-spill format from Drift simulation model
    if "spills" in drift_data and len(drift_data["spills"]) > 0:
        spill = drift_data["spills"][0]
        spill_id = spill.get("spill_id", drift_data.get("status", "SPILL_001"))
        
        # Coordinates
        prob_source = spill.get("probable_source", {})
        source_lat = prob_source.get("latitude", 0.0)
        source_lon = prob_source.get("longitude", 0.0)
        
        # Spatial threshold
        radius_km = spill.get("spatial_uncertainty_km", 5.0)
        
        # Time parsing
        time_info = spill.get("source_time_window", {})
        est_time_str = time_info.get("estimated_spill_time")
        uncertainty_hrs = time_info.get("uncertainty_hours", 6)
        
        if est_time_str:
            est_dt = datetime.fromisoformat(est_time_str.replace("Z", "+00:00"))
            time_start = est_dt - timedelta(hours=uncertainty_hrs)
            time_end = est_dt + timedelta(hours=uncertainty_hrs)
        else:
            time_start = datetime.now(timezone.utc) - timedelta(hours=12)
            time_end = datetime.now(timezone.utc) + timedelta(hours=12)
            
        return spill_id, source_lat, source_lon, time_start, time_end, radius_km

    # Single slick standard schema fallback
    spill_id = drift_data.get("spill_id", "SPILL_MOCK_001")
    origin = drift_data.get("estimated_spill_origin", {})
    source_lat = origin.get("lat", 0.0)
    source_lon = origin.get("lon", 0.0)
    
    time_window = drift_data.get("time_window", {})
    start_str = time_window.get("start")
    end_str = time_window.get("end")
    
    time_start = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else datetime.now(timezone.utc) - timedelta(hours=6)
    time_end = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else datetime.now(timezone.utc) + timedelta(hours=6)
    
    radius_km = drift_data.get("drift_radius_km", 5.0)
    return spill_id, source_lat, source_lon, time_start, time_end, radius_km

def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    drift_file = os.path.join(base_dir, "data", "mock_drift_input.json")
    ais_file = os.path.join(base_dir, "data", "raw_ais_sample.csv")
    output_dir = os.path.join(base_dir, "output")
    output_file = os.path.join(output_dir, "candidate_vessels.json")

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(drift_file) or not os.path.exists(ais_file):
        print(f"[AIS Engine] Missing input files in data directory.")
        return

    with open(drift_file, 'r') as f:
        drift_data = json.load(f)

    spill_id, s_lat, s_lon, t_start, t_end, threshold_km = parse_drift_input(drift_data)
    print(f"[AIS Engine] Loaded Spill Origin: ({s_lat}, {s_lon}) | Window: {t_start.isoformat()} to {t_end.isoformat()} | Threshold: {threshold_km} km")

    # Load and standardize AIS dataframe
    df = pd.read_csv(ais_file)
    
    # Standardize column names (lat/latitude, lon/longitude)
    rename_cols = {}
    if 'latitude' in df.columns:
        rename_cols['latitude'] = 'lat'
    if 'longitude' in df.columns:
        rename_cols['longitude'] = 'lon'
    if rename_cols:
        df = df.rename(columns=rename_cols)

    # Clean missing fields
    df = df.dropna(subset=['mmsi', 'lat', 'lon', 'timestamp'])
    df['mmsi'] = df['mmsi'].astype(str)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values(by=['mmsi', 'timestamp'])

    # Spatiotemporal correlation
    candidates = []
    grouped = df.groupby('mmsi')

    for mmsi, group in grouped:
        trajectory = []
        min_dist = float('inf')
        points_in_window = 0
        speeds = []
        courses = []

        vessel_name = group['vessel_name'].iloc[0] if 'vessel_name' in group.columns else f"Vessel_{mmsi}"
        vessel_type = group['vessel_type'].iloc[0] if 'vessel_type' in group.columns else "Unknown"

        for _, row in group.iterrows():
            lat = row['lat']
            lon = row['lon']
            ts = row['timestamp']
            spd = row.get('speed', 0.0)
            crs = row.get('course', 0.0)

            speeds.append(spd)
            courses.append(crs)

            dist = haversine_distance(lat, lon, s_lat, s_lon)
            if dist < min_dist:
                min_dist = dist

            if t_start <= ts <= t_end and dist <= threshold_km:
                points_in_window += 1

            trajectory.append({
                "timestamp": ts.isoformat(),
                "lat": round(lat, 5),
                "lon": round(lon, 5)
            })

        # Calculate time spent near source (assuming approximate 30-60 min sampling intervals)
        time_spent_min = points_in_window * 60

        # AIS gap detection (flag gaps > 2 hours)
        ais_gap = False
        time_diffs = group['timestamp'].diff().dt.total_seconds() / 3600.0
        if (time_diffs > 2.0).any():
            ais_gap = True

        # If vessel was within spatial threshold during the time window, add as candidate
        if min_dist <= threshold_km:
            candidates.append({
                "mmsi": mmsi,
                "vessel_name": vessel_name,
                "vessel_type": vessel_type,
                "minimum_distance_km": round(min_dist, 2),
                "source_window_presence": points_in_window > 0,
                "time_spent_near_source_min": time_spent_min,
                "average_speed": round(float(pd.Series(speeds).mean()), 1) if speeds else 0.0,
                "course": round(float(pd.Series(courses).mean()), 1) if courses else 0.0,
                "ais_gap_detected": ais_gap,
                "trajectory": trajectory
            })

    output_payload = {
        "spill_id": spill_id,
        "total_candidates_identified": len(candidates),
        "candidates": candidates
    }

    with open(output_file, 'w') as f:
        json.dump(output_payload, f, indent=2)

    print(f"[AIS Engine] Processed {len(grouped)} vessels. Found {len(candidates)} suspect candidate(s).")
    print(f"[AIS Engine] Output written to {output_file}")

if __name__ == "__main__":
    run_pipeline()