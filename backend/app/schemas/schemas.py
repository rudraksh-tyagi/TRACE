"""
TRACE - Marine Oil Spill Intelligence System

Shared Pydantic data contracts.

Phase 1:
    Detection -> GIS -> Drift -> AIS -> Backend -> Frontend

Phase 2:
    Attribution Engine consumes the shared contracts and
    produces explainable vessel attribution scores.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# COMMON GEOGRAPHIC MODELS
# ============================================================


class Coordinate(BaseModel):
    """Latitude / longitude coordinate."""

    model_config = ConfigDict(extra="forbid")

    lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees.",
    )

    lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees.",
    )


class BoundingBox(BaseModel):
    """Geographic bounding box."""

    model_config = ConfigDict(extra="forbid")

    min_lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Minimum latitude.",
    )

    min_lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Minimum longitude.",
    )

    max_lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Maximum latitude.",
    )

    max_lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Maximum longitude.",
    )


# ============================================================
# ROLE 1 -> GIS
# DETECTION RESULT
# ============================================================


class DetectionResult(BaseModel):
    """
    Role 1 AI/ML detection result.

    Current college prototype:
        Sentinel-1 SAR
            ↓
        -28 dB threshold
            ↓
        Connected-component filtering
            ↓
        oil_mask.tif
    """

    model_config = ConfigDict(extra="forbid")

    spill_id: str = Field(
        ...,
        min_length=1,
        description="Unique spill/detection identifier.",
    )

    detected: bool = Field(
        ...,
        description="Whether potential oil pixels were detected.",
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional detection confidence between 0 and 1.",
    )

    acquisition_timestamp: datetime = Field(
        ...,
        description="Sentinel-1 image acquisition timestamp.",
    )

    source_image: str = Field(
        ...,
        description="Source Sentinel-1 SAR image.",
    )

    mask_path: str = Field(
        ...,
        description="Generated georeferenced oil mask path.",
    )

    threshold_db: float = Field(
        default=-28.0,
        description="SAR backscatter threshold.",
    )

    minimum_component_area_pixels: int = Field(
        default=5000,
        gt=0,
        description="Minimum connected component size.",
    )

    detected_pixels: int = Field(
        ...,
        ge=0,
        description="Number of detected candidate oil pixels.",
    )

    detected_pixel_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of raster pixels detected as candidate oil.",
    )

    crs: str = Field(
        ...,
        description="Coordinate reference system of the raster.",
    )

    raster_width: int = Field(
        ...,
        gt=0,
        description="Raster width in pixels.",
    )

    raster_height: int = Field(
        ...,
        gt=0,
        description="Raster height in pixels.",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional detection metadata.",
    )


# ============================================================
# ROLE 2 GIS -> BACKEND
# SPILL
# ============================================================


class SpillSchema(BaseModel):
    """GIS-derived oil-spill geometry and spatial properties."""

    model_config = ConfigDict(extra="forbid")

    spill_id: str = Field(
        ...,
        min_length=1,
        description="Unique spill identifier.",
    )

    detected: bool = Field(
        ...,
        description="Whether a spill region was detected.",
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional detection confidence.",
    )

    timestamp: datetime = Field(
        ...,
        description="Source SAR acquisition timestamp.",
    )

    centroid: Coordinate = Field(
        ...,
        description="Geographic centroid of the spill.",
    )

    area_km2: float = Field(
        ...,
        ge=0.0,
        description="Physical spill area in square kilometres.",
    )

    perimeter_km: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Spill perimeter in kilometres.",
    )

    polygon_geojson: Dict[str, Any] = Field(
        ...,
        description="GeoJSON Feature or Geometry of the spill.",
    )

    bounding_box: Optional[BoundingBox] = Field(
        default=None,
        description="Geographic bounding box.",
    )


# ============================================================
# ROLE 3 DRIFT
# ============================================================


class TimeWindow(BaseModel):
    """Estimated spill-source time window."""

    model_config = ConfigDict(extra="forbid")

    start_time: datetime = Field(
        ...,
        description="Start of source time window.",
    )

    end_time: datetime = Field(
        ...,
        description="End of source time window.",
    )


class DriftTrackPoint(BaseModel):
    """Single drift trajectory point."""

    model_config = ConfigDict(extra="forbid")

    lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude.",
    )

    lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude.",
    )

    timestamp: datetime = Field(
        ...,
        description="Trajectory timestamp.",
    )


class ForecastTrack(BaseModel):
    """One forward drift trajectory."""

    model_config = ConfigDict(extra="forbid")

    points: List[DriftTrackPoint] = Field(
        default_factory=list,
        description="Ordered forecast trajectory points.",
    )


class DriftSchema(BaseModel):
    """Drift/source reconstruction output."""

    model_config = ConfigDict(extra="forbid")

    origin_coordinates: Coordinate = Field(
        ...,
        description="Estimated spill source coordinates.",
    )

    source_time_window: TimeWindow = Field(
        ...,
        description="Estimated source time window.",
    )

    uncertainty_radius_km: float = Field(
        ...,
        ge=0.0,
        description="Uncertainty radius around estimated source.",
    )

    backward_track: List[DriftTrackPoint] = Field(
        default_factory=list,
        description="Hindcast trajectory.",
    )

    forecast_tracks: List[ForecastTrack] = Field(
        default_factory=list,
        description="Forward predicted trajectories.",
    )


# ============================================================
# ROLE 4 AIS -> ROLE 5
# VESSEL
# ============================================================


class VesselTrajectoryPoint(BaseModel):
    """
    Single cleaned AIS trajectory observation.

    IMPORTANT:
    Speed and course are vessel-level features in the current
    Role 4 contract, not trajectory-point fields.
    """

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(
        ...,
        description="AIS observation timestamp.",
    )

    lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude.",
    )

    lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude.",
    )


class VesselSchema(BaseModel):
    """
    Role 4 -> Role 5 candidate vessel contract.

    These are the cleaned/extracted AIS features that the
    attribution engine consumes.
    """

    model_config = ConfigDict(extra="forbid")

    spill_id: str = Field(
        ...,
        min_length=1,
        description="Spill identifier associated with this candidate.",
    )

    mmsi: str = Field(
        ...,
        min_length=9,
        max_length=9,
        description="9-digit Maritime Mobile Service Identity.",
    )

    vessel_name: str = Field(
        default="Unknown",
        description="Vessel name or Unknown.",
    )

    vessel_type: str = Field(
        ...,
        description="Vessel type such as Tanker, Cargo, Tug, Fishing.",
    )

    minimum_distance_km: float = Field(
        ...,
        ge=0.0,
        description="Closest vessel-to-source distance in kilometres.",
    )

    source_window_presence: bool = Field(
        ...,
        description="Whether vessel was present during source window.",
    )

    time_spent_near_source_min: int = Field(
        default=0,
        ge=0,
        description="Minutes spent near the estimated source.",
    )

    average_speed: float = Field(
        ...,
        ge=0.0,
        description="Average vessel speed over ground in knots.",
    )

    course: float = Field(
        ...,
        ge=0.0,
        lt=360.0,
        description="Mean course over ground in degrees.",
    )

    ais_gap_detected: bool = Field(
        default=False,
        description="Whether a significant AIS gap was detected.",
    )

    trajectory: List[VesselTrajectoryPoint] = Field(
        default_factory=list,
        description="Cleaned chronological AIS trajectory.",
    )


# ============================================================
# ATTRIBUTION
# ============================================================


class ComponentScores(BaseModel):
    """Individual attribution components."""

    model_config = ConfigDict(extra="forbid")

    distance_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Distance/proximity score.",
    )

    time_compatibility_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Source-window compatibility score.",
    )

    trajectory_consistency_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Trajectory consistency score.",
    )

    behavior_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="AIS behavior anomaly score.",
    )


class AttributionSchema(BaseModel):
    """Final explainable attribution result."""

    model_config = ConfigDict(extra="forbid")

    mmsi: str = Field(
        ...,
        min_length=1,
        description="Candidate vessel MMSI.",
    )

    vessel_identity: Optional[str] = Field(
        default=None,
        description="Human-readable vessel identity.",
    )

    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall attribution score as percentage.",
    )

    component_scores: ComponentScores = Field(
        ...,
        description="Breakdown of attribution score.",
    )

    explanations: List[str] = Field(
        default_factory=list,
        description="Human-readable scoring evidence.",
    )


# ============================================================
# MASTER INCIDENT
# ============================================================


class IncidentMetadata(BaseModel):
    """Incident generation metadata."""

    model_config = ConfigDict(extra="forbid")

    generation_timestamp: datetime = Field(
        ...,
        description="Time at which incident analysis was generated.",
    )

    system_version: str = Field(
        ...,
        description="TRACE system version.",
    )


class MasterIncidentResponse(BaseModel):
    """Unified TRACE incident response."""

    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(
        ...,
        description="Unique incident identifier.",
    )

    spill: SpillSchema = Field(
        ...,
        description="GIS spill information.",
    )

    drift: DriftSchema = Field(
        ...,
        description="Drift/source reconstruction.",
    )

    ranked_candidates: List[AttributionSchema] = Field(
        default_factory=list,
        description="Vessels ranked by attribution score.",
    )

    metadata: IncidentMetadata = Field(
        ...,
        description="Incident metadata.",
    )