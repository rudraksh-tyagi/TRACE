# TRACE — Tracking & Remote-sensing Analytics for Contaminant Events

**TRACE** is an end-to-end AI-powered marine oil-spill intelligence system that detects oil slicks from Sentinel-1 SAR satellite imagery, vectorizes polygons in GIS, projects forward and backward drift trajectories using oceanographic vectors, and correlates historical AIS vessel telemetry to identify and rank potential source vessels.

---

## 1. Target System Architecture

```
                                ┌─────────────────────────┐
                                │     Frontend (React)    │
                                └────────────┬────────────┘
                                             │ HTTP API
                                             ▼
                                ┌─────────────────────────┐
                                │   FastAPI Backend API   │
                                │  (Central Orchestrator) │
                                └────────────┬────────────┘
                                             │
     ┌──────────────────┬────────────────────┴────────────────────┬──────────────────┐
     ▼                  ▼                                         ▼                  ▼
┌─────────┐   ┌──────────────────┐                       ┌─────────────────┐  ┌──────────────┐
│  AI/ML  │   │  GIS Vectorizer  │                       │   Drift Model   │  │  AIS Engine  │
│ (Role 1)│   │     (Role 2)     │                       │    (Role 3)     │  │   (Role 4)   │
└────┬────┘   └─────────┬────────┘                       └────────┬────────┘  └──────┬───────┘
     │                  │                                         │                  │
 oil_mask.tif   spill_polygons.geojson                   output_drift.json  candidate_vessels.json
     │                  │                                         │                  │
     └──────────────────┴────────────────────┬────────────────────┴──────────────────┘
                                             ▼
                                ┌─────────────────────────┐
                                │   Attribution Engine    │
                                │   (Role 5 / Backend)    │
                                └────────────┬────────────┘
                                             ▼
                                ┌─────────────────────────┐
                                │ MasterIncidentResponse  │
                                │   (State Persistence)   │
                                └─────────────────────────┘
```

---

## 2. Folder Responsibilities

* **`frontend/`**: Modern React SPA interface built with Vite, Lucide icons, dynamic Leaflet maritime maps, candidate vessel spotlight cards, trajectory logs, and score breakdowns.
* **`backend/`**: FastAPI web server & central orchestrator. Houses data models (`app/schemas/schemas.py`), deterministic Attribution Engine (`app/services/attribution_engine.py`), pipeline orchestrator (`app/services/pipeline_orchestrator.py`), state persistence manager (`app/services/state_manager.py`), and REST endpoints.
* **`ai_ml/`**: Role 1 oil spill detection engine. Processes Sentinel-1 SAR imagery using backscatter thresholding (-28 dB) and connected-component filtering to output georeferenced `oil_mask.tif` and `detection_metadata.json`.
* **`gis_vectorizer.py`**: Role 2 GIS vectorization engine. Converts raster mask into WGS84 GeoJSON polygons (`spill_polygons.geojson`), computing centroid, bounding box, perimeter, and physical area (Mollweide projection ESRI:54009).
* **`drift_model/`**: Role 3 oceanographic drift simulation engine. Computes 12-hour forward forecasts and 12-hour backward hindcasts using wind leeway factor and ocean current vectors, producing `output_drift.json`.
* **`ais_engine/`**: Role 4 AIS telemetry processing pipeline. Filters historical vessel tracks by Haversine proximity and time bounds, detecting AIS transponder gaps and exporting `candidate_vessels.json`.
* **`outputs/`**: Standardized directory holding intermediate and final artifacts (`oil_mask.tif`, `detection_metadata.json`, `spill_polygons.geojson`, `output_drift.json`).

---

## 3. End-to-End Data Flow

1. **User Action / API Trigger**: User accesses frontend dashboard or submits `POST /api/orchestrate`.
2. **AI/ML Detection**: `ai_ml` threshold detector extracts oil candidate pixels from Sentinel-1 SAR image and generates `outputs/oil_mask.tif`.
3. **GIS Vectorization**: `gis_vectorizer.py` extracts WGS84 polygon boundaries, centroid, and area (km²) into `outputs/spill_polygons.geojson`.
4. **Drift Prediction**: `drift_model` calculates forward forecast and backward hindcast trajectories, estimating probable spill origin into `outputs/output_drift.json`.
5. **AIS Correlation**: `ais_engine` reads drift origin and time bounds, evaluates raw vessel tracks, and extracts suspect vessels into `ais_engine/output/candidate_vessels.json`.
6. **Vessel Attribution**: Backend Attribution Engine computes deterministic scores across **Distance (35%)**, **Time Compatibility (25%)**, **Trajectory Consistency (25%)**, and **Behavioral AIS Gaps (15%)**.
7. **Result Delivery**: Backend persists unified `MasterIncidentResponse` and serves real-time visualization data to the frontend dashboard.

---

## 4. Backend API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server status check & mock mode flag |
| `GET` | `/api/incident/complete` | Complete unified TRACE incident response |
| `GET` | `/api/incident` | Latest active investigation session |
| `GET` | `/api/spill` | GIS spill geometry & spatial parameters |
| `GET` | `/api/drift` | Reconstructed drift tracks & uncertainty radius |
| `GET` | `/api/vessels` | AIS candidate vessel telemetry & tracks |
| `GET` | `/api/attribution` | Ranked vessel attribution scores & explanations |
| `POST` | `/api/orchestrate` | Trigger complete end-to-end processing pipeline |
| `POST` | `/api/run-pipeline` | Run attribution engine (auto-orchestrates if missing) |
| `DELETE`| `/api/incidents` | Reset all investigation sessions |

---

## 5. Environment Variables

### Backend (`backend/.env`)
```ini
USE_MOCK_DATA=false
LOG_LEVEL=INFO
CORS_ORIGINS=*
PORT=8000
```

### Frontend (`frontend/.env`)
```ini
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 6. Installation & Setup

### Prerequisites
* Python 3.10+
* Node.js 18+ and npm

### 1. Install Backend Dependencies
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

---

## 7. How to Run the Complete Project

### Terminal 1: Run FastAPI Backend
```bash
cd backend
# Using virtual environment python:
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```
*Backend API will be available at: `http://127.0.0.1:8000`*
*Interactive API Docs: `http://127.0.0.1:8000/docs`*

### Terminal 2: Run React Frontend
```bash
cd frontend
npm run dev
```
*Frontend Application will be available at: `http://localhost:5173`*

---

## 8. Example API Request & Response

### Request: Trigger End-to-End Orchestration
```bash
curl -X POST "http://127.0.0.1:8000/api/orchestrate" \
     -H "Content-Type: application/json" \
     -d '{}'
```

### Response Payload:
```json
{
  "status": "success",
  "message": "TRACE end-to-end pipeline orchestrated successfully.",
  "incident_id": "spill_001",
  "candidate_count": 3,
  "top_candidate": {
    "mmsi": "413123456",
    "vessel_identity": "PACIFIC STAR",
    "overall_score": 88.75,
    "component_scores": {
      "distance_score": 88.0,
      "time_compatibility_score": 92.5,
      "trajectory_consistency_score": 85.0,
      "behavior_score": 100.0
    },
    "explanations": [
      "Vessel passed approximately 1.20 km from the estimated spill origin.",
      "Vessel was in very close proximity to the estimated spill source.",
      "Vessel was present during the estimated source time window.",
      "AIS transponder gap greater than 60 minutes was detected near the source."
    ]
  },
  "incident": { ... }
}
```

---

## 9. Troubleshooting

* **Backend Unreachable in Frontend**: Ensure FastAPI is running on port 8000 and `VITE_API_BASE_URL` in `frontend/.env` points to `http://127.0.0.1:8000`.
* **Missing GeoTIFF Raster Mask**: The pipeline orchestrator (`pipeline_orchestrator.py`) automatically generates a valid sample raster at `outputs/oil_mask.tif` if no raw satellite image is placed in `ai_ml/data/`.
* **CORS Errors**: Verify `CORS_ORIGINS=*` is set in `backend/.env`.
