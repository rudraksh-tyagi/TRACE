import os
import json
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

def run_gis_vectorization(
    metadata_path="outputs/detection_metadata.json",
    output_geojson_path="outputs/spill_polygons.geojson"
):
    # 1. Load Role 1's JSON metadata
    if not os.path.exists(metadata_path):
        print(f"❌ Error: Could not find '{metadata_path}'. Make sure Role 1 has run their pipeline!")
        return

    with open(metadata_path, "r") as f:
        role1_metadata = json.load(f)

    tif_path = role1_metadata.get("mask_file", "outputs/oil_mask.tif")

    if not os.path.exists(tif_path):
        print(f"❌ Error: Could not find raster mask at '{tif_path}'")
        return

    print(f"🌐 Processing Role 1 mask: {tif_path} ...")

    features = []

    # 2. Read Georeferenced GeoTIFF Mask from Role 1
    with rasterio.open(tif_path) as src:
        mask_data = src.read(1)
        transform_matrix = src.transform
        src_crs = src.crs

        # Transformer to WGS84 (EPSG:4326 Lat/Lon)
        project_to_wgs84 = pyproj.Transformer.from_crs(
            src_crs, "EPSG:4326", always_xy=True
        ).transform

        # Transformer to Equal Area Projection (ESRI:54009) for accurate sq km area calculation
        project_to_mollweide = pyproj.Transformer.from_crs(
            src_crs, "ESRI:54009", always_xy=True
        ).transform

        # Extract polygon boundaries where pixel == 1 (Potential Oil)
        results = shapes(mask_data, mask=(mask_data == 1), transform=transform_matrix)

        spill_counter = 1

        for geom_dict, val in results:
            geom_native = shape(geom_dict)
            
            if geom_native.is_empty:
                continue

            # Convert to Lat/Lon coordinates (WGS84)
            if src_crs != "EPSG:4326":
                geom_wgs84 = transform(project_to_wgs84, geom_native)
            else:
                geom_wgs84 = geom_native

            # Calculate physical area in sq km and perimeter in km
            geom_projected = transform(project_to_mollweide, geom_native)
            area_km2 = round(geom_projected.area / 1e6, 3)
            perimeter_km = round(geom_projected.length / 1000, 3)

            # Centroid & Bounding Box
            centroid_lon_lat = [round(geom_wgs84.centroid.x, 5), round(geom_wgs84.centroid.y, 5)]
            bbox = [round(coord, 5) for coord in geom_wgs84.bounds]

            # Construct GeoJSON Feature connected with Role 1 parameters
            feature = {
                "type": "Feature",
                "properties": {
                    "spill_id": f"spill_{spill_counter:03d}",
                    "source_image": role1_metadata.get("source_image", "Unknown"),
                    "detected_oil_pixels": role1_metadata.get("detected_oil_pixels", 0),
                    "detected_area_percentage": role1_metadata.get("detected_area_percentage", 0),
                    "threshold_db": role1_metadata.get("detection_method", {}).get("threshold_db", -28),
                    "area_km2": area_km2,
                    "perimeter_km": perimeter_km,
                    "centroid_lon_lat": centroid_lon_lat,
                    "bbox_minx_miny_maxx_maxy": bbox
                },
                "geometry": geom_wgs84.__geo_interface__
            }

            features.append(feature)
            spill_counter += 1

    # 3. Output GeoJSON Payload for Role 3 & Role 4
    geojson_payload = {
        "type": "FeatureCollection",
        "metadata_source": metadata_path,
        "total_spills_found": len(features),
        "features": features
    }

    os.makedirs(os.path.dirname(output_geojson_path), exist_ok=True)
    with open(output_geojson_path, "w") as f:
        json.dump(geojson_payload, f, indent=2)

    print(f"✅ Handoff Complete! Extracted {len(features)} polygon region(s) and saved to '{output_geojson_path}'")

if __name__ == "__main__":
    run_gis_vectorization()