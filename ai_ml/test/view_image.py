import rasterio
import matplotlib.pyplot as plt
import numpy as np

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "data/raw/Radar_data/test/masks/2018_09_26.tif"

# Read satellite image
with rasterio.open(image_path) as src:
    image = src.read(1)

# Read ground-truth mask
with rasterio.open(mask_path) as src:
    mask = src.read(1)

print("Image shape:", image.shape)
print("Image min:", np.min(image))
print("Image max:", np.max(image))

print("Mask shape:", mask.shape)
print("Mask values:", np.unique(mask))

# Display image and mask
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.imshow(image, cmap="gray")
plt.title("Sentinel-1 SAR Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(mask, cmap="gray")
plt.title("Ground Truth Oil-Spill Mask")
plt.axis("off")

plt.tight_layout()
plt.show()