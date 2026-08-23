import json
from datetime import datetime, timedelta

def load_input_json(file_path):
    """Reads and parses input JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_drift_output(output_file_path, spill_id, detection_time_str, forward_traj, backward_traj, uncertainty_km=5.0):
    """
    Formats simulation results into a standardized schema and writes to a JSON file.
    """
    # Parse initial detection time string (e.g. '2026-08-23T10:00:00Z')
    # If standard ISO string has 'Z', replace it for datetime parsing
    clean_time_str = detection_time_str.replace("Z", "")
    base_time = datetime.fromisoformat(clean_time_str)
    
    # Calculate estimated source time (backward duration based on last point in backward trajectory)
    back_hours = backward_traj[-1]["hour"]
    source_time = base_time - timedelta(hours=back_hours)
    
    # Extract probable source coordinates (last point of backward trajectory)
    probable_source = {
        "latitude": backward_traj[-1]["lat"],
        "longitude": backward_traj[-1]["lon"]
    }
    
    # Format final dictionary
    output_data = {
        "spill_id": spill_id,
        "detection_timestamp": detection_time_str,
        "probable_source": probable_source,
        "source_time_window": {
            "estimated_spill_time": source_time.isoformat() + "Z",
            "uncertainty_hours": back_hours
        },
        "spatial_uncertainty_km": uncertainty_km,
        "trajectories": {
            "forward_forecast": forward_traj,
            "backward_hindcast": backward_traj
        }
    }
    
    # Write formatted JSON to file
    with open(output_file_path, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Successfully saved drift forecast output to: {output_file_path}")