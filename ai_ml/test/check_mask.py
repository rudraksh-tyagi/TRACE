import rasterio

original = "data/raw/Radar_data/test/images/2018_09_26.tif"
mask = "oil_mask.tif"

with rasterio.open(original) as src:
    print("ORIGINAL SAR")
    print("CRS:", src.crs)
    print("Transform:", src.transform)
    print("Shape:", src.height, src.width)

with rasterio.open(mask) as src:
    print("\nOIL MASK")
    print("CRS:", src.crs)
    print("Transform:", src.transform)
    print("Shape:", src.height, src.width)