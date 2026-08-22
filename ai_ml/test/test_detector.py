import rasterio
import numpy as np
import cv2
import os

image_folder = "data/raw/Radar_data/test/images"
mask_folder = "data/raw/Radar_data/test/masks"

threshold = -28
min_area = 5000

# Test these three images
test_files = [
    "2018_12_19_d.tif",
    "2018_12_19_e.tif",
    "2018_12_19_f_.tif"
]

for filename in test_files:

    image_path = os.path.join(image_folder, filename)
    mask_path = os.path.join(mask_folder, filename)

    print("\n================================")
    print(filename)
    print("================================")

    # Read image
    with rasterio.open(image_path) as src:
        image = src.read(1)

    # Read ground truth
    with rasterio.open(mask_path) as src:
        ground_truth = src.read(1)

    ground_truth_bool = ground_truth == 1

    # Step 1: threshold
    prediction = (image < threshold).astype(np.uint8)

    # Step 2: connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        prediction,
        connectivity=8
    )

    # Step 3: remove small regions
    cleaned = np.zeros_like(prediction)

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned[labels == label] = 1

    prediction_bool = cleaned == 1

    # Calculate metrics
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

    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"Dice:      {dice:.3f}")