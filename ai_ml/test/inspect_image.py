import rasterio
import numpy as np

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "data/raw/Radar_data/test/masks/2018_09_26.tif"

with rasterio.open(image_path) as src:
    image = src.read(1)

with rasterio.open(mask_path) as src:
    mask = src.read(1)

# Separate pixels using the ground-truth mask
oil_pixels = image[mask == 1]
background_pixels = image[mask == 0]

print("OIL PIXELS")
print("Count:", len(oil_pixels))
print("Mean:", np.mean(oil_pixels))
print("Median:", np.median(oil_pixels))
print("Min:", np.min(oil_pixels))
print("Max:", np.max(oil_pixels))

print("\nBACKGROUND PIXELS")
print("Count:", len(background_pixels))
print("Mean:", np.mean(background_pixels))
print("Median:", np.median(background_pixels))
print("Min:", np.min(background_pixels))
print("Max:", np.max(background_pixels))