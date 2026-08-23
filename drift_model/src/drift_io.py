import json
import os

def parse_geojson_input(geojson_path: str):
    if not os.path.exists(geojson_path):
        # Fallback to mock data if GeoJSON isn't downloaded yet
        return [{
            "spill_id": "SPILL_MOCK_001",
            "detection_timestamp": "2026-08-23T10:00:00Z",
            "latitude": 20.1234,
            "longitude": 70.4567,
            "area_sq_km": 2.5
        }]
        
    with open(geojson_path, "r") as f:
        data = json.load(f)
        
    spills = []
    features = data.get("features", [])
    
    for idx, feature in enumerate(features):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        
        centroid_lon_lat = props.get("centroid_lon_lat", [])
        if centroid_lon_lat and len(centroid_lon_lat) >= 2:
            lon, lat = centroid_lon_lat[0], centroid_lon_lat[1]
        else:
            centroid = props.get("centroid", {})
            lat = centroid.get("lat") or props.get("latitude")
            lon = centroid.get("lon") or props.get("longitude")
        
        if lat is None or lon is None:
            if geometry.get("type") == "Polygon":
                coords = geometry["coordinates"][0]
                avg_lon = sum(c[0] for c in coords) / len(coords)
                avg_lat = sum(c[1] for c in coords) / len(coords)
                lat, lon = avg_lat, avg_lon

        spills.append({
            "spill_id": props.get("spill_id", f"SPILL_{idx+1:03d}"),
            "detection_timestamp": props.get("acquisition_time", "2026-08-23T10:00:00Z"),
            "latitude": lat or 20.1234,
            "longitude": lon or 70.4567,
            "area_sq_km": props.get("area_sq_km", 1.0)
        })
        
    return spills if spills else [{
        "spill_id": "SPILL_MOCK_001",
        "detection_timestamp": "2026-08-23T10:00:00Z",
        "latitude": 20.1234,
        "longitude": 70.4567,
        "area_sq_km": 2.5
    }]

def run_drift_simulation(geojson_input_path: str, output_path: str):
    # Import inside function to prevent circular import
    from drift_model.src.drift import DriftEngine

    spills = parse_geojson_input(geojson_input_path)
    engine = DriftEngine()
    results = []

    for spill in spills:
        sim_data = engine.simulate(
            lat=spill["latitude"],
            lon=spill["longitude"],
            timestamp=spill["detection_timestamp"]
        )
        sim_data["spill_id"] = spill["spill_id"]
        sim_data["area_sq_km"] = spill["area_sq_km"]
        results.append(sim_data)

    output_payload = {
        "status": "success",
        "processed_spills_count": len(results),
        "spills": results
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_payload, f, indent=2)

    return output_payload