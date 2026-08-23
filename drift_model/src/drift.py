import sys
import os
import math

# Add current directory (src/) to Python's search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from drift_io import load_input_json, save_drift_output

def load_default_config(config_path):
    """Loads physical and simulation constants from central config JSON."""
    if os.path.exists(config_path):
        return load_input_json(config_path)
    # Fallback default configuration if file is missing
    return {
        "physics": {
            "earth_radius_m": 6371000.0,
            "wind_leeway_factor": 0.03,
            "current_factor": 1.0
        },
        "simulation": {
            "default_spatial_uncertainty_km": 5.0
        }
    }

def compass_to_math_radians(degree):
    """Converts marine compass bearing (0 deg = North) to mathematical radians (0 rad = East)."""
    math_degree = (90.0 - degree) % 360.0
    return math.radians(math_degree)

def update_position(lat, lon, v_x, v_y, dt_seconds, earth_radius_m):
    """Updates latitude and longitude using displacement over dt seconds."""
    dx = v_x * dt_seconds
    dy = v_y * dt_seconds
    
    d_lat_rad = dy / earth_radius_m
    d_lon_rad = dx / (earth_radius_m * math.cos(math.radians(lat)))
    
    new_lat = lat + math.degrees(d_lat_rad)
    new_lon = lon + math.degrees(d_lon_rad)
    return new_lat, new_lon

def run_drift_simulation(input_file_path, output_file_path, config_file_path="drift_model/config/default_config.json"):
    # 1. Load Configurations and Inputs
    config = load_default_config(config_file_path)
    data = load_input_json(input_file_path)
    
    earth_radius = config["physics"]["earth_radius_m"]
    wind_factor = config["physics"]["wind_leeway_factor"]
    current_factor = config["physics"]["current_factor"]
    uncertainty_km = config["simulation"].get("default_spatial_uncertainty_km", 5.0)
    
    spill_id = data["spill_id"]
    detection_time = data["detection_timestamp"]
    start_lat = data["location"]["latitude"]
    start_lon = data["location"]["longitude"]
    
    wind_speed = data["environmental_forcing"]["wind"]["speed_m_s"]
    wind_dir = data["environmental_forcing"]["wind"]["direction_deg"]
    
    current_speed = data["environmental_forcing"]["current"]["speed_m_s"]
    current_dir = data["environmental_forcing"]["current"]["direction_deg"]
    
    duration_hours = data["simulation_config"]["duration_hours"]
    dt = data["simulation_config"]["time_step_seconds"]
    
    # 2. Compute Velocity Components (m/s)
    w_rad = compass_to_math_radians(wind_dir)
    c_rad = compass_to_math_radians(current_dir)
    
    v_x = (wind_factor * wind_speed * math.cos(w_rad)) + (current_factor * current_speed * math.cos(c_rad))
    v_y = (wind_factor * wind_speed * math.sin(w_rad)) + (current_factor * current_speed * math.sin(c_rad))
    
    # 3. Forward Simulation
    curr_lat, curr_lon = start_lat, start_lon
    forward_trajectory = [{"hour": 0, "lat": curr_lat, "lon": curr_lon}]
    
    steps = int((duration_hours * 3600) / dt)
    for step in range(1, steps + 1):
        curr_lat, curr_lon = update_position(curr_lat, curr_lon, v_x, v_y, dt, earth_radius)
        forward_trajectory.append({"hour": step, "lat": round(curr_lat, 4), "lon": round(curr_lon, 4)})
        
    # 4. Backward Hindcast Simulation
    back_lat, back_lon = start_lat, start_lon
    backward_trajectory = [{"hour": 0, "lat": back_lat, "lon": back_lon}]
    
    for step in range(1, steps + 1):
        back_lat, back_lon = update_position(back_lat, back_lon, -v_x, -v_y, dt, earth_radius)
        backward_trajectory.append({"hour": step, "lat": round(back_lat, 4), "lon": round(back_lon, 4)})

    # 5. Export Output via I/O module
    save_drift_output(
        output_file_path=output_file_path,
        spill_id=spill_id,
        detection_time_str=detection_time,
        forward_traj=forward_trajectory,
        backward_traj=backward_trajectory,
        uncertainty_km=uncertainty_km
    )

if __name__ == "__main__":
    input_path = "drift_model/tests/data/mock_spill.json"
    output_path = "drift_model/tests/data/output_drift.json"
    config_path = "drift_model/config/default_config.json"
    
    run_drift_simulation(input_path, output_path, config_path)