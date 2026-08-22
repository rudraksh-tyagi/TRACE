import rasterio
import numpy as np
import cv2
import os


# ============================================================
# CONFIGURATION
# ============================================================

THRESHOLD = -28
MIN_AREA = 5000

INPUT_IMAGE = "data/raw/Radar_data/test/images/2018_09_26.tif"

OUTPUT_MASK = "outputs/oil_mask.tif"


# ============================================================
# LOAD SAR IMAGE
# ============================================================

with rasterio.open(INPUT_IMAGE) as src:

    image = src.read(1)

    # Save the original geospatial information
    profile = src.profile


# ============================================================
# STEP 1 — OIL CANDIDATE DETECTION
# ============================================================

prediction = (image < THRESHOLD).astype(np.uint8)


# ============================================================
# STEP 2 — CONNECTED COMPONENT FILTERING
# ============================================================

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    prediction,
    connectivity=8
)

cleaned = np.zeros_like(prediction)

for label in range(1, num_labels):

    area = stats[label, cv2.CC_STAT_AREA]

    if area >= MIN_AREA:
        cleaned[labels == label] = 1


# ============================================================
# STEP 3 — SAVE GEOSPATIAL MASK
# ============================================================

profile.update(
    dtype=rasterio.uint8,
    count=1,
    nodata=0
)

with rasterio.open(OUTPUT_MASK, "w", **profile) as dst:

    dst.write(cleaned, 1)


# ============================================================
# SUMMARY
# ============================================================

oil_pixels = np.sum(cleaned == 1)
total_pixels = cleaned.size

percentage = (oil_pixels / total_pixels) * 100

print("--------------------------------")
print("Oil Spill Detection Complete")
print("--------------------------------")

print(f"Input image: {INPUT_IMAGE}")
print(f"Threshold: {THRESHOLD} dB")
print(f"Minimum component area: {MIN_AREA} pixels")

print(f"Detected oil pixels: {oil_pixels}")
print(f"Detected area percentage: {percentage:.2f}%")

print(f"Output mask: {OUTPUT_MASK}")