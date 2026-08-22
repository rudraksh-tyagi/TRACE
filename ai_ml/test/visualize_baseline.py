import rasterio
import numpy as np
import matplotlib.pyplot as plt

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "data/raw/Radar_data/test/masks/2018_09_26.tif"

with rasterio.open(image_path) as src:
    image = src.read(1)

with rasterio.open(mask_path) as src:
    ground_truth = src.read(1)

# Our baseline detector
threshold = -28
prediction = image < threshold

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.imshow(image, cmap="gray")
plt.title("Sentinel-1 SAR")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(ground_truth, cmap="gray")
plt.title("Ground Truth")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(prediction, cmap="gray")
plt.title("Our Baseline Detection")
plt.axis("off")

plt.tight_layout()
plt.show()