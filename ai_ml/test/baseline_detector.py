import rasterio
import numpy as np

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "data/raw/Radar_data/test/masks/2018_09_26.tif"

with rasterio.open(image_path) as src:
    image = src.read(1)

with rasterio.open(mask_path) as src:
    mask = src.read(1)

# Ground truth: 1 = oil, 0 = background
ground_truth = mask == 1

thresholds = [-28, -27, -26, -25, -24, -23]

for threshold in thresholds:

    # Lower SAR value = potential oil
    prediction = image < threshold

    true_positive = np.sum(prediction & ground_truth)
    false_positive = np.sum(prediction & ~ground_truth)
    false_negative = np.sum(~prediction & ground_truth)

    precision = true_positive / (true_positive + false_positive + 1e-10)
    recall = true_positive / (true_positive + false_negative + 1e-10)

    dice = (
        2 * true_positive /
        (2 * true_positive + false_positive + false_negative + 1e-10)
    )

    print(f"\nThreshold: {threshold}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"Dice:      {dice:.3f}")