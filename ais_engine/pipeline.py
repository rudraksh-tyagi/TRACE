import json
import math
import pandas as pd
from datetime import timedelta

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def run_pipeline():
    df = pd.read_csv("ais_engine/data/raw_ais_sample.csv")
    with open("ais_engine/data/mock_drift_input.json") as f:
        drift = json.load(f)

    # 1. Read coordinates and search radius
    if "probable_source" in drift:
        origin_lat = drift["probable_source"]["latitude"]
        origin_lon = drift["probable_source"]["longitude"]
    else:
        origin_lat = drift.get("origin_lat", 20.2788)
        origin_lon = drift.get("origin_lon", 70.1016)

    max_radius = drift.get("spatial_uncertainty_km", drift.get("uncertainty_radius_km", 5.0))

    # 2. Compute dynamic time window
    time_cfg = drift.get("source_time_window", {})
    if "start" in time_cfg and "end" in time_cfg:
        t_start = pd.to_datetime(time_cfg["start"], utc=True)
        t_end = pd.to_datetime(time_cfg["end"], utc=True)
    elif "estimated_spill_time" in time_cfg:
        center_time = pd.to_datetime(time_cfg["estimated_spill_time"], utc=True)
        hours = time_cfg.get("uncertainty_hours", 12)
        t_start = center_time - timedelta(hours=hours)
        t_end = center_time + timedelta(hours=hours)
    else:
        t_start = pd.to_datetime("2026-08-22T14:00:00Z", utc=True)
        t_end = pd.to_datetime("2026-08-23T02:00:00Z", utc=True)

    # 3. Clean and filter AIS records
    df = df.dropna(subset=['mmsi', 'latitude', 'longitude', 'timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df[(df['latitude'].between(-90, 90)) & (df['longitude'].between(-180, 180))]
    df = df.drop_duplicates(subset=['mmsi', 'timestamp']).sort_values(by=['mmsi', 'timestamp'])

    candidates = []

    for mmsi, group in df.groupby('mmsi'):
        group['dist'] = group.apply(lambda r: haversine(r['latitude'], r['longitude'], origin_lat, origin_lon), axis=1)
        min_dist = float(group['dist'].min())

        if min_dist > max_radius:
            continue

        window_points = group[(group['timestamp'] >= t_start) & (group['timestamp'] <= t_end)]
        source_window_presence = not window_points.empty

        inside_points = group[group['dist'] <= max_radius]
        time_spent_min = len(inside_points) * 15

        traj = [
            {
                "timestamp": r['timestamp'].isoformat(),
                "lat": round(float(r['latitude']), 4),
                "lon": round(float(r['longitude']), 4)
            }
            for _, r in group.iterrows()
        ]

        candidates.append({
            "mmsi": str(mmsi),
            "vessel_name": str(group['vessel_name'].iloc[0]),
            "vessel_type": str(group['vessel_type'].iloc[0]),
            "minimum_distance_km": round(min_dist, 2),
            "source_window_presence": source_window_presence,
            "time_spent_near_source_min": time_spent_min,
            "average_speed": round(float(group['speed'].mean()), 2),
            "course": round(float(group['course'].mean()), 1),
            "ais_gap_detected": bool((group['timestamp'].diff().dt.total_seconds() > 3600).any()),
            "trajectory": traj
        })

    output = {
        "spill_id": drift.get("spill_id", "SPILL_MOCK_001"),
        "candidates": candidates
    }
    with open("ais_engine/output/candidate_vessels.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Pipeline executed successfully! Found {len(candidates)} candidate vessel(s).")

if __name__ == "__main__":
    run_pipeline()
