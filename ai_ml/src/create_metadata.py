import json
import os
from datetime import datetime

metadata = {
    "spill_detected": True,
    "source_image": "2018_09_26.tif",
    "mask_file": "outputs/oil_mask.tif",

    "detection_method": {
        "type": "SAR threshold + connected component filtering",
        "threshold_db": -28,
        "minimum_component_area_pixels": 5000
    },

    "detected_oil_pixels": 350491,
    "detected_area_percentage": 2.70,

    "processing_status": "completed"
}

output_file = "outputs/detection_metadata.json"

with open(output_file, "w") as f:
    json.dump(metadata, f, indent=4)

print("--------------------------------")
print("Metadata Created")
print("--------------------------------")
print(f"File: {output_file}")