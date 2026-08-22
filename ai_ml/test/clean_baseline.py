import rasterio
import numpy as np
import cv2

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "data/raw/Radar_data/test/masks/2018_09_26.tif"

# Read image
with rasterio.open(image_path) as src:
    image = src.read(1)

# Read ground truth
with rasterio.open(mask_path) as src:
    ground_truth = src.read(1)

ground_truth_bool = ground_truth == 1

# Fixed detection threshold
threshold = -28

# Initial detection
prediction = (image < threshold).astype(np.uint8)

# Find connected components
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    prediction,
    connectivity=8
)

# Test different minimum component sizes
min_areas = [100, 250, 500, 1000, 2000, 5000]

for min_area in min_areas:

    cleaned = np.zeros_like(prediction)

    # Keep only sufficiently large regions
    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned[labels == label] = 1

    prediction_bool = cleaned == 1

    true_positive = np.sum(prediction_bool & ground_truth_bool)
    false_positive = np.sum(prediction_bool & ~ground_truth_bool)
    false_negative = np.sum(~prediction_bool & ground_truth_bool)

    precision = true_positive / (
        true_positive + false_positive + 1e-10
    )

    recall = true_positive / (
        true_positive + false_negative + 1e-10
    )

    dice = (
        2 * true_positive /
        (2 * true_positive + false_positive + false_negative + 1e-10)
    )

    print(f"\nMinimum area: {min_area}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"Dice:      {dice:.3f}")