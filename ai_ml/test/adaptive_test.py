import rasterio
import numpy as np
import cv2
import os

image_folder = "data/raw/Radar_data/test/images"
mask_folder = "data/raw/Radar_data/test/masks"

min_area = 5000

test_files = [
    "2018_09_26.tif",
    "2018_12_19_d.tif",
    "2018_12_19_e.tif",
    "2018_12_19_f_.tif"
]

for filename in test_files:

    image_path = os.path.join(image_folder, filename)
    mask_path = os.path.join(mask_folder, filename)

    with rasterio.open(image_path) as src:
        image = src.read(1)

    with rasterio.open(mask_path) as src:
        ground_truth = src.read(1)

    # Adaptive threshold
    median = np.median(image)
    threshold = median - 6

    # Detect dark regions
    prediction = (image < threshold).astype(np.uint8)

    # Connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        prediction,
        connectivity=8
    )

    # Remove small regions
    cleaned = np.zeros_like(prediction)

    for label in range(1, num_labels):

        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned[labels == label] = 1

    ground_truth_bool = ground_truth == 1
    prediction_bool = cleaned == 1

    true_positive = np.sum(
        prediction_bool & ground_truth_bool
    )

    false_positive = np.sum(
        prediction_bool & ~ground_truth_bool
    )

    false_negative = np.sum(
        ~prediction_bool & ground_truth_bool
    )

    precision = true_positive / (
        true_positive + false_positive + 1e-10
    )

    recall = true_positive / (
        true_positive + false_negative + 1e-10
    )

    dice = (
        2 * true_positive /
        (
            2 * true_positive
            + false_positive
            + false_negative
            + 1e-10
        )
    )

    print("\n==============================")
    print(filename)
    print("==============================")
    print(f"Median:    {median:.2f}")
    print(f"Threshold: {threshold:.2f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"Dice:      {dice:.3f}")