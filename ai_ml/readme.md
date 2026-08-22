# Role 1 — Oil-Spill Detection

## Overview

Role 1 is responsible for the first stage of the TRACE pipeline: detecting potential oil-spill regions from Sentinel-1 SAR satellite imagery.

For the college-level SIH prototype, a SAR backscatter thresholding approach with connected-component filtering was developed to produce a georeferenced oil-spill candidate mask for the GIS module.

## Work Completed

### 1. Dataset Analysis

The provided Sentinel-1 SAR images and corresponding ground-truth oil-spill masks were inspected and analyzed.

Primary development image:

- `2018_09_26.tif`
- Size: `2555 × 5083`
- Data type: `float32`
- CRS: `EPSG:32616`
- Value range: approximately `-36.45` to `20.96`
- Median: approximately `-22.04`

Ground-truth mask:

- `0` = background
- `1` = oil-spill region

### 2. Baseline Detection

The SAR image was analyzed to identify darker/lower-backscatter regions associated with the labeled oil-spill area.

A threshold-based detector was developed:

```text
Sentinel-1 SAR Image
        ↓
Backscatter Threshold
        ↓
Potential Oil Pixels
```

Different thresholds were tested, including `-28`, `-27`, `-26`, `-25`, `-24`, and `-23 dB`.

The `-28 dB` threshold provided the best result for the primary development scene.

Initial result:

- Precision: `0.893`
- Recall: `0.814`
- Dice: `0.852`

### 3. Noise Removal

The initial threshold mask contained small isolated detections.

Connected-component filtering was added to remove small regions.

Different minimum component areas were tested, including:

- 100 pixels
- 250 pixels
- 500 pixels
- 1000 pixels
- 2000 pixels
- 5000 pixels

The selected prototype configuration is:

- Threshold: `-28 dB`
- Minimum component area: `5000 pixels`

Result on the primary development scene:

- Precision: `0.964`
- Recall: `0.795`
- Dice: `0.871`

### 4. Testing on Additional Scenes

The fixed detector was tested on additional Sentinel-1 scenes.

This showed that a fixed threshold does not perform equally well across different SAR scenes. An adaptive threshold based on the image median was also investigated, but its performance remained inconsistent.

For the college-level prototype, the fixed baseline was retained because it provides a simple and explainable detection pipeline that can be integrated with the rest of the system.

## 5. Final Detection Pipeline

```text
Sentinel-1 SAR Image
        ↓
    -28 dB Threshold
        ↓
 Binary Detection Mask
        ↓
Connected-Component Filtering
        ↓
Potential Oil-Spill Mask
```

Main implementation:

`src/oil_detector.py`

## 6. Output

The primary output is:

`outputs/oil_mask.tif`

The mask is binary:

- `0` = background / not detected
- `1` = potential oil-spill pixel

The generated mask preserves the spatial information of the original SAR image:

- CRS: `EPSG:32616`
- Shape: `2555 × 5083`
- Transform: same as the source SAR image

For the primary development scene:

- Detected oil pixels: `350491`
- Detected raster-pixel percentage: `2.70%`

The `2.70%` value represents the percentage of raster pixels classified as candidate oil pixels. It is not the physical oil-spill area in square kilometres. Geographic area calculation is handled by the GIS module.

## 7. Supporting Outputs

Role 1 also generates:

- `detection_metadata.json` — information about the detection and processing parameters.
- `detection_preview.png` — visualization of the SAR image and detected candidate region.

These outputs are used for verification, debugging, and demonstration.

## 8. Role 1 → Role 2 Handoff

```text
Sentinel-1 SAR
      ↓
Role 1 — Oil-Spill Detection
      ↓
outputs/oil_mask.tif
      ↓
Role 2 — GIS Processing
```

Role 1 determines:

**Which pixels are potential oil-spill pixels?**

Role 2 uses the georeferenced mask to determine:

- Spill polygon
- Location
- Area
- Centroid
- Bounding box
- Other spatial characteristics

## 9. Repository Structure

```text
ai_ml/
├── data/
│   └── README.md
│
├── models/
│
├── outputs/
│   ├── oil_mask.tif
│   ├── detection_metadata.json
│   └── detection_preview.png
│
├── src/
│   ├── oil_detector.py
│   ├── create_metadata.py
│   └── create_preview.py
│
├── test/
│   ├── baseline_detector.py
│   ├── adaptive_test.py
│   ├── clean_baseline.py
│   ├── inspect_image.py
│   ├── check_mask.py
│   ├── test_detector.py
│   ├── test.py
│   ├── view_image.py
│   └── visualize_baseline.py
│
└── README.md
```

## 10. Current Status

Completed:

- [x] Sentinel-1 SAR dataset inspection
- [x] Ground-truth analysis
- [x] SAR threshold experimentation
- [x] Baseline oil-spill detector
- [x] Connected-component noise removal
- [x] Multi-scene testing
- [x] Adaptive threshold investigation
- [x] Georeferenced oil-spill mask generation
- [x] Metadata generation
- [x] Detection visualization
- [x] Role 2 output handoff

### Current Prototype Configuration

- Threshold: `-28 dB`
- Minimum component area: `5000 pixels`
- Primary development Dice: `0.871`

The Role 1 oil-spill detection component is complete for the current college-level SIH prototype.

The current detector is a prototype computer-vision baseline. A trained ML segmentation model can be added later if required without changing the downstream mask-based interface.
