# Role 4 — AIS Data Processing & Spatiotemporal Correlation Engine

## Overview
This module ingests raw historical Automatic Identification System (AIS) vessel telemetry, performs data cleaning/sanitization, and executes a spatiotemporal trajectory correlation against the estimated oil spill source and drift hindcast window.

---

## Directory Structure
ais_engine/
├── data/
│   ├── mock_drift_input.json   # Drift hindcast source coordinates & time bounds
│   └── raw_ais_sample.csv       # Cleaned sample AIS vessel telemetry
├── output/
│   └── candidate_vessels.json  # Filtered suspect vessels & trajectory data
├── pipeline.py                 # Core processing, Haversine filtering & scoring logic
└── README.md

---

## Pipeline Workflow
1. Data Cleaning: Removes records missing critical identifiers (mmsi, lat, lon, timestamp), filters invalid geographic coordinates, and drops duplicate pings.
2. Dynamic Schema Parser: Supports variable drift hindcast inputs (both explicit time windows and center-time/uncertainty-hour models).
3. Haversine Distance Metric: Computes real-time vessel-to-spill proximity across interpolated track points.
4. Spatiotemporal Filtering: Flags vessels present within the uncertainty radius (R <= 5 km) during the active spill time window.
5. Output Contract: Exports standardized JSON with candidate metadata, average speed/course, AIS gap flags, and trajectory coordinates ready for backend ingestion.

---

## How to Run

source venv/bin/activate
python3 ais_engine/pipeline.py