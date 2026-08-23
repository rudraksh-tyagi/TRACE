# 🌊 Module 3: Oil Spill Drift Modeling Engine

Core engine for simulating 2D physical advection trajectories of marine oil slicks using forward forecasting and backward hindcasting vector mechanics.

---

## 📐 1. Physical Mechanics

The engine applies a 2D kinematic Lagrangian particle tracking model:

$$\vec{V}_{\text{drift}} = \vec{V}_{\text{current}} + \alpha \cdot \vec{V}_{\text{wind}}$$

* **Ocean Currents ($\vec{V}_{\text{current}}$):** $100\%$ velocity vector advection.
* **Wind Leeway ($\alpha$):** $3.0\%$ empirical transfer factor.

---

## 🏗️ 2. Project Structure

```text
drift_model/
├── config/
│   └── default_config.json      # Simulation parameters
├── src/
│   ├── drift.py                 # Trajectory math & physics engine
│   └── drift_io.py              # Schema validation & JSON parser
├── tests/
│   ├── data/
│   │   ├── mock_spill.json      # Sample input payload
│   │   └── output_drift.json    # Standardized output fixture
│   └── test_drift.py            # Automated test suite
└── README.md


3. Data Contracts
A. Input Payload (From Role 2)

    latitude (Float)

    longitude (Float)

    detection_timestamp (ISO 8601 UTC)

B. Output Schema (output_drift.json)

Used by Role 4 (AIS) and Role 5 (Backend/UI):
{
  "spill_id": "SPILL_MOCK_001",
  "detection_timestamp": "2026-08-23T10:00:00Z",
  "probable_source": {
    "latitude": 20.2788,
    "longitude": 70.1016
  },
  "source_time_window": {
    "estimated_spill_time": "2026-08-23T02:00:00Z",
    "start_time_utc": "2026-08-22T14:00:00Z",
    "end_time_utc": "2026-08-23T02:00:00Z",
    "uncertainty_hours": 12
  },
  "spatial_uncertainty_km": 5.0,
  "trajectories": {
    "forward_forecast": [
      { "hour": 0, "lat": 20.1234, "lon": 70.4567 },
      { "hour": 12, "lat": 20.0123, "lon": 70.8910 }
    ],
    "backward_hindcast": [
      { "hour": 0, "lat": 20.1234, "lon": 70.4567 },
      { "hour": 12, "lat": 20.2788, "lon": 70.1016 }
    ]
  }
}