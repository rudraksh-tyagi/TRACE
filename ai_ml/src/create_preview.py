import rasterio
import matplotlib.pyplot as plt

image_path = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask_path = "outputs/oil_mask.tif"

with rasterio.open(image_path) as src:
    image = src.read(1)

with rasterio.open(mask_path) as src:
    mask = src.read(1)

plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.imshow(image, cmap="gray")
plt.title("Sentinel-1 SAR")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(mask, cmap="gray")
plt.title("Detected Oil-Spill Mask")
plt.axis("off")

plt.tight_layout()

output_file = "outputs/detection_preview.png"

plt.savefig(output_file, dpi=150, bbox_inches="tight")

print("--------------------------------")
print("Detection Preview Created")
print("--------------------------------")
print(f"File: {output_file}")