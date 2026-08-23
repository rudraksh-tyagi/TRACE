# TRACE
TRACE — Tracking & Remote-sensing Analytics for Contaminant Events. An AI-powered marine oil-spill intelligence system that detects oil slicks from satellite imagery, traces their movement using oceanographic data, and correlates historical AIS vessel trajectories to identify and rank potential source vessels.

For prototype, hum input ko 3 categories mein rakhenge:

A. Spill information

spill_id
spill location
detection timestamp

B. Environmental conditions

wind speed
wind direction
current speed
current direction

C. Simulation settings

simulation duration
time step

Here is your **PHASE 1 WORKFLOW & SUMMARY LOG**. You can keep this record to track your module's development progress.

---

### PHASE 1 LOG — Physics Fundamentals & Core Engine (`drift.py`)

**1. Objective**

Build a lightweight, standalone Python drift simulation script (`drift_model/src/drift.py`) capable of computing time-series forward predictions and backward hindcasts using environmental forcing parameters (wind and ocean currents).

---

**2. Key Features Implemented**

* **Compass-to-Cartesian Angle Conversion:** Automatically converts marine compass bearings ($0^\circ = \text{North}$, clockwise) into mathematical angles ($0^\circ = \text{East}$, counter-clockwise) in radians for trigonometric accuracy.
* **Vector Mechanics (Wind + Current):** Combines ocean currents ($100\%$ velocity) and surface wind leeway factor ($3\%$ velocity) into combined orthogonal velocity components ($v_x, v_y$) in $\text{m/s}$.
* **Spherical Earth Position Updates:** Converts displacement in meters ($\Delta x, \Delta y$) into geographic coordinates ($\Delta \text{lat}, \Delta \text{lon}$) using Earth's mean radius ($R = 6,371,000\text{m}$).
* **Forward Forecast Simulation:** Iteratively projects the future trajectory of the oil slick hour-by-hour over a configurable duration (e.g., $+12\text{ hours}$).
* **Backward Hindcast Simulation:** Inverts velocity vectors ($-v_x, -v_y$) to rewind the simulation backward in time (e.g., $-12\text{ hours}$) to pinpoint the **probable source region**.

---

**3. Execution & Verification**

* **Input File:** `drift_model/tests/data/mock_spill.json`
* **Test Command:** `python3 drift_model/src/drift.py`
* **Verified Output:**
* **Initial Location:** Lat $20.1234$, Lon $70.4567$
* **Forecast ($+12\text{h}$):** Lat $19.9680$, Lon $70.8115$
* **Probable Source ($-12\text{h}$):** Lat $20.2788$, Lon $70.1016$



---




### PHASE 2 LOG — Output Exporter & Data Pipeline (`drift_io.py`)

**1. What We Did**

* Created a dedicated I/O module (`drift_model/src/drift_io.py`) to handle file reading and writing.
* Connected `drift.py` with `drift_io.py` so the calculated math gets saved automatically into a structured `output_drift.json` file.

**2. Why We Did It**

* **Interoperability:** Terminal prints are useless for other system components. Generating `output_drift.json` allows Role 4 (AIS Pipeline) and Role 5 (Backend APIs) to read source coordinates and time windows directly.
* **Separation of Concerns:** `drift.py` handles pure physics equations, while `drift_io.py` handles data parsing and JSON creation.

**3. Key Features Created**

* **Time Inversion:** Calculates exact historical spill timestamp by subtracting backward step duration from satellite detection time ($T_{\text{source}} = T_{\text{detection}} - 12\text{h}$).
* **Trajectory Structuring:** Formats continuous hourly array points into clean JSON arrays (`forward_forecast` and `backward_hindcast`).
* **Uncertainty Radius:** Integrates standard spatial uncertainty bounds ($\pm 5.0\text{ km}$) into output schemas.

**4. Generated Artifact Check**
Open `drift_model/tests/data/output_drift.json` in VS Code to see your clean data payload:

```json
{
    "spill_id": "SPILL_001",
    "detection_timestamp": "2026-08-23T10:00:00Z",
    "probable_source": {
        "latitude": 20.2788,
        "longitude": 70.1016
    },
    "source_time_window": {
        "estimated_spill_time": "2026-08-23T02:00:00Z",
        "uncertainty_hours": 12
    },
    "spatial_uncertainty_km": 5.0,
    "trajectories": {
        "forward_forecast": [ ... ],
        "backward_hindcast": [ ... ]
    }
}

```

---



### PHASE 3 LOG — Config Isolation & Automated Unit Testing

**1. What We Did**

* Extracted physical and simulation parameters out of Python scripts into `drift_model/config/default_config.json`.
* Refactored `drift.py` and `update_position()` to consume configurations dynamically.
* Created an automated test suite (`drift_model/tests/test_drift.py`) to validate math conversions and vector mechanics.

**2. Why We Did It**

* **Zero Hardcoded Parameters:** Hardcoded magic numbers (`0.03`, `6371000`) make code fragile. Config files allow real-time parameter tuning without touching core code.
* **Production Integrity:** Automated unit testing verifies that trigonometric conversions (marine to cartesian) and zero-displacement boundary cases work error-free before deployment.

**3. Key Features Added**

* **Centralized Configuration:** Config file now drives Earth radius, wind leeway factor, current factor, and default spatial uncertainty ($5.0\text{ km}$).
* **Automated Unit Tests:** `test_drift.py` verifies `compass_to_math_radians()` trigonometric logic and zero-movement velocity assertions in `update_position()`.

**4. Execution Verification**

* **Config-driven Drift Simulation:** `python3 drift_model/src/drift.py` $\rightarrow$ Successfully outputted to `output_drift.json`.
* **Automated Unit Testing:** `python3 drift_model/tests/test_drift.py` $\rightarrow$ Printed `All unit tests passed successfully!`.

---






