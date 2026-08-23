"""
TRACE - Static Mock Data

Phase 1 / Phase 2 development data.

All vessel, drift and GIS values in this file are SYNTHETIC
demonstration data.

Role 1 detection metadata is based on the current prototype
detector configuration.
"""

from datetime import datetime, timezone

from app.schemas.schemas import (
    DetectionResult,
    DriftSchema,
    DriftTrackPoint,
    ForecastTrack,
    IncidentMetadata,
    MasterIncidentResponse,
    SpillSchema,
    TimeWindow,
    VesselSchema,
    VesselTrajectoryPoint,
)


# ============================================================
# CONSTANTS
# ============================================================

SPILL_ID = "SP001"

INCIDENT_ID = "INC-2026-001"

SYSTEM_VERSION = "TRACE-0.1.0"


# ============================================================
# ROLE 1 - AI/ML DETECTION
# ============================================================

MOCK_DETECTION = DetectionResult(
    spill_id=SPILL_ID,

    detected=True,

    confidence=0.871,

    acquisition_timestamp=datetime(
        2018,
        9,
        26,
        10,
        42,
        tzinfo=timezone.utc,
    ),

    source_image="2018_09_26.tif",

    mask_path="outputs/oil_mask.tif",

    threshold_db=-28.0,

    minimum_component_area_pixels=5000,

    detected_pixels=350491,

    detected_pixel_percentage=2.70,

    crs="EPSG:32616",

    raster_width=5083,

    raster_height=2555,

    metadata={
        "detector_type": "SAR threshold + connected components",
        "threshold_db": -28.0,
        "minimum_component_area_pixels": 5000,
        "precision": 0.964,
        "recall": 0.795,
        "dice": 0.871,
        "mask_value": 1,
        "background_value": 0,
        "mask_file": "outputs/oil_mask.tif",
        "preview_file": "outputs/detection_preview.png",
        "metadata_file": "outputs/detection_metadata.json",
    },
)


# ============================================================
# ROLE 2 - GIS
# ============================================================

MOCK_SPILL = SpillSchema(
    spill_id=SPILL_ID,

    detected=True,

    confidence=0.871,

    timestamp=datetime(
        2018,
        9,
        26,
        10,
        42,
        tzinfo=timezone.utc,
    ),

    centroid={
        "lat": 25.1842,
        "lon": -89.7421,
    },

    area_km2=14.72,

    perimeter_km=18.43,

    polygon_geojson={
        "type": "Feature",
        "properties": {
            "spill_id": SPILL_ID,
            "source": "oil_mask.tif",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-89.7560, 25.1750],
                    [-89.7420, 25.1715],
                    [-89.7280, 25.1775],
                    [-89.7240, 25.1900],
                    [-89.7360, 25.1980],
                    [-89.7510, 25.1950],
                    [-89.7590, 25.1850],
                    [-89.7560, 25.1750],
                ]
            ],
        },
    },

    bounding_box={
        "min_lat": 25.1715,
        "min_lon": -89.7590,
        "max_lat": 25.1980,
        "max_lon": -89.7240,
    },
)


# ============================================================
# ROLE 3 - DRIFT
# ============================================================

MOCK_DRIFT = DriftSchema(
    origin_coordinates={
        "lat": 25.1625,
        "lon": -89.7810,
    },

    source_time_window=TimeWindow(
        start_time=datetime(
            2018,
            9,
            25,
            18,
            0,
            tzinfo=timezone.utc,
        ),

        end_time=datetime(
            2018,
            9,
            26,
            6,
            0,
            tzinfo=timezone.utc,
        ),
    ),

    uncertainty_radius_km=4.8,

    backward_track=[
        DriftTrackPoint(
            lat=25.1625,
            lon=-89.7810,
            timestamp=datetime(
                2018,
                9,
                25,
                18,
                0,
                tzinfo=timezone.utc,
            ),
        ),

        DriftTrackPoint(
            lat=25.1670,
            lon=-89.7750,
            timestamp=datetime(
                2018,
                9,
                25,
                21,
                0,
                tzinfo=timezone.utc,
            ),
        ),

        DriftTrackPoint(
            lat=25.1740,
            lon=-89.7660,
            timestamp=datetime(
                2018,
                9,
                26,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        ),

        DriftTrackPoint(
            lat=25.1810,
            lon=-89.7540,
            timestamp=datetime(
                2018,
                9,
                26,
                3,
                0,
                tzinfo=timezone.utc,
            ),
        ),
    ],

    forecast_tracks=[
        ForecastTrack(
            points=[
                DriftTrackPoint(
                    lat=25.1842,
                    lon=-89.7421,
                    timestamp=datetime(
                        2018,
                        9,
                        26,
                        10,
                        42,
                        tzinfo=timezone.utc,
                    ),
                ),

                DriftTrackPoint(
                    lat=25.1910,
                    lon=-89.7310,
                    timestamp=datetime(
                        2018,
                        9,
                        26,
                        14,
                        42,
                        tzinfo=timezone.utc,
                    ),
                ),

                DriftTrackPoint(
                    lat=25.1990,
                    lon=-89.7190,
                    timestamp=datetime(
                        2018,
                        9,
                        26,
                        18,
                        42,
                        tzinfo=timezone.utc,
                    ),
                ),
            ]
        )
    ],
)


# ============================================================
# ROLE 4 - AIS CANDIDATES
#
# IMPORTANT:
# Speed/course are vessel-level fields.
# They are NOT inside trajectory points.
# ============================================================

MOCK_VESSELS = [

    # --------------------------------------------------------
    # Candidate 1
    # --------------------------------------------------------

    VesselSchema(
        spill_id=SPILL_ID,

        mmsi="367890123",

        vessel_name="Ocean Meridian",

        vessel_type="Tanker",

        minimum_distance_km=0.52,

        source_window_presence=True,

        time_spent_near_source_min=75,

        average_speed=10.3,

        course=63.0,

        ais_gap_detected=True,

        trajectory=[
            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    22,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1580,
                lon=-89.7760,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    0,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1620,
                lon=-89.7700,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    2,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1690,
                lon=-89.7580,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    4,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1780,
                lon=-89.7480,
            ),
        ],
    ),

    # --------------------------------------------------------
    # Candidate 2
    # --------------------------------------------------------

    VesselSchema(
        spill_id=SPILL_ID,

        mmsi="367812456",

        vessel_name="Gulf Carrier",

        vessel_type="Cargo",

        minimum_distance_km=2.31,

        source_window_presence=True,

        time_spent_near_source_min=40,

        average_speed=12.7,

        course=51.0,

        ais_gap_detected=False,

        trajectory=[
            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    20,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1400,
                lon=-89.8200,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    23,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1510,
                lon=-89.8010,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    2,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1620,
                lon=-89.7820,
            ),
        ],
    ),

    # --------------------------------------------------------
    # Candidate 3
    # --------------------------------------------------------

    VesselSchema(
        spill_id=SPILL_ID,

        mmsi="367745321",

        vessel_name="Blue Horizon",

        vessel_type="Tanker",

        minimum_distance_km=5.74,

        source_window_presence=False,

        time_spent_near_source_min=0,

        average_speed=10.5,

        course=93.0,

        ais_gap_detected=False,

        trajectory=[
            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    18,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.2400,
                lon=-89.6900,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    0,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.2300,
                lon=-89.7050,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    6,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.2180,
                lon=-89.7200,
            ),
        ],
    ),

    # --------------------------------------------------------
    # Candidate 4
    # --------------------------------------------------------

    VesselSchema(
        spill_id=SPILL_ID,

        mmsi="367654987",

        vessel_name="Atlantic Trader",

        vessel_type="Cargo",

        minimum_distance_km=7.92,

        source_window_presence=False,

        time_spent_near_source_min=0,

        average_speed=13.8,

        course=43.0,

        ais_gap_detected=False,

        trajectory=[
            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    16,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.0900,
                lon=-89.8500,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    25,
                    22,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1050,
                lon=-89.8350,
            ),

            VesselTrajectoryPoint(
                timestamp=datetime(
                    2018,
                    9,
                    26,
                    4,
                    0,
                    tzinfo=timezone.utc,
                ),
                lat=25.1200,
                lon=-89.8200,
            ),
        ],
    ),
]


# ============================================================
# INCIDENT METADATA
# ============================================================

MOCK_METADATA = IncidentMetadata(
    generation_timestamp=datetime.now(timezone.utc),
    system_version=SYSTEM_VERSION,
)


# ============================================================
# INITIAL MASTER INCIDENT
#
# Ranked candidates are intentionally empty here.
# Phase 2 attribution engine fills them dynamically.
# ============================================================

MOCK_INCIDENT = MasterIncidentResponse(
    incident_id=INCIDENT_ID,

    spill=MOCK_SPILL,

    drift=MOCK_DRIFT,

    ranked_candidates=[],

    metadata=MOCK_METADATA,
)