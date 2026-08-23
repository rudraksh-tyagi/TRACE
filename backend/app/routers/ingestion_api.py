"""
TRACE - Pipeline Ingestion & Orchestration API

Phase 2 - Part 2 + Part 3

Responsibilities:

    Role 2 GIS
        -> POST /api/ingest/spill

    Role 3 Drift
        -> POST /api/ingest/drift

    Role 4 AIS
        -> POST /api/ingest/vessels

    Orchestration
        -> POST /api/run-pipeline

    Incident State
        -> GET /api/incident
        -> GET /api/incident/{spill_id}
        -> GET /api/pipeline-result

    Demo Reset
        -> DELETE /api/incident/{spill_id}
        -> DELETE /api/incidents

Current architecture:

    Upstream modules
          ↓
    Temporary pipeline state
          ↓
    Attribution Engine
          ↓
    MasterIncidentResponse
          ↓
    IncidentStateManager
          ↓
    Memory + incidents/*.json
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.schemas import (
    AttributionSchema,
    DriftSchema,
    MasterIncidentResponse,
    SpillSchema,
    VesselSchema,
)

from app.services.attribution_engine import rank_vessels
from app.services.state_manager import state_manager
from app.config.settings import settings
from app.exceptions import PipelineStateError


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("trace.ingestion")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api",
    tags=["Pipeline Ingestion"],
)


# ============================================================
# TEMPORARY PIPELINE INPUT STATE
# ============================================================

class PipelineInputStore:
    """
    Temporary buffer for upstream pipeline outputs.

    This is NOT the incident database.

    It only holds the latest:

        GIS spill
        Drift result
        AIS candidates

    until /api/run-pipeline is executed.

    The final consolidated incident is handled by
    IncidentStateManager.
    """

    def __init__(self) -> None:

        self.spill: Optional[SpillSchema] = None

        self.drift: Optional[DriftSchema] = None

        self.vessels: List[VesselSchema] = []


# One input buffer for the running application.
pipeline_inputs = PipelineInputStore()


# ============================================================
# RESPONSE MODELS
# ============================================================

class IngestionResponse(BaseModel):
    """Standard upstream ingestion response."""

    status: str = Field(
        ...,
        description="Operation status.",
    )

    message: str = Field(
        ...,
        description="Human-readable operation result.",
    )

    spill_id: str = Field(
        ...,
        description="Spill/incident associated with the data.",
    )

    cached_incident_invalidated: bool = Field(
        default=True,
        description=(
            "Whether previously generated incident state "
            "was invalidated."
        ),
    )


class VesselIngestionResponse(BaseModel):
    """Response returned after AIS ingestion."""

    status: str = Field(
        ...,
        description="Operation status.",
    )

    message: str = Field(
        ...,
        description="Human-readable operation result.",
    )

    spill_id: str = Field(
        ...,
        description="Spill associated with candidate vessels.",
    )

    vessel_count: int = Field(
        ...,
        ge=0,
        description="Number of candidate vessels stored.",
    )

    cached_incident_invalidated: bool = Field(
        default=True,
        description="Whether previous incident state was invalidated.",
    )


class PipelineRunResponse(BaseModel):
    """Response returned after running the complete pipeline."""

    status: str = Field(
        ...,
        description="Pipeline execution status.",
    )

    message: str = Field(
        ...,
        description="Human-readable pipeline result.",
    )

    incident_id: str = Field(
        ...,
        description="Generated incident identifier.",
    )

    candidate_count: int = Field(
        ...,
        ge=0,
        description="Number of attributed candidate vessels.",
    )

    top_candidate: Optional[AttributionSchema] = Field(
        default=None,
        description="Highest-ranked candidate.",
    )

    incident: MasterIncidentResponse = Field(
        ...,
        description="Complete generated incident.",
    )


# ============================================================
# HELPERS
# ============================================================

def validate_same_spill_id(
    expected_spill_id: str,
    actual_spill_id: str,
    source: str,
) -> None:
    """
    Ensure pipeline modules are referring to the same incident.
    """

    if expected_spill_id != actual_spill_id:

        logger.error(
            "%s spill ID mismatch | expected=%s | received=%s",
            source,
            expected_spill_id,
            actual_spill_id,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{source} data belongs to spill "
                f"'{actual_spill_id}', but the active "
                f"spill is '{expected_spill_id}'."
            ),
        )


def get_active_spill_id() -> Optional[str]:
    """Return the currently loaded upstream spill ID."""

    if pipeline_inputs.spill is None:
        return None

    return pipeline_inputs.spill.spill_id


def invalidate_previous_incident(
    spill_id: str,
) -> None:
    """
    Remove an old consolidated incident when new upstream
    information arrives.

    This prevents the frontend from accidentally displaying
    stale attribution results.
    """

    try:

        existed = state_manager.clear_incident(
            spill_id
        )

        if existed:

            logger.info(
                "Previous incident invalidated | spill_id=%s",
                spill_id,
            )

    except RuntimeError:

        logger.exception(
            "Failed to invalidate previous incident | "
            "spill_id=%s",
            spill_id,
        )


# ============================================================
# INGEST GIS SPILL
# ============================================================

@router.post(
    "/ingest/spill",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest GIS spill result",
)
async def ingest_spill(
    spill: SpillSchema,
) -> IngestionResponse:
    """
    Receive the GIS-derived spill geometry.

    Role 2 provides:

        - centroid
        - polygon GeoJSON
        - bounding box
        - area
        - perimeter
        - confidence
    """

    logger.info(
        "GIS handoff received | spill_id=%s | "
        "area=%.2f km2 | confidence=%s",
        spill.spill_id,
        spill.area_km2,
        spill.confidence,
    )

    # Store latest GIS result.
    pipeline_inputs.spill = spill

    # New upstream data invalidates old final results.
    invalidate_previous_incident(
        spill.spill_id
    )

    logger.info(
        "GIS spill stored successfully | spill_id=%s",
        spill.spill_id,
    )

    return IngestionResponse(
        status="success",
        message="GIS spill data ingested successfully.",
        spill_id=spill.spill_id,
        cached_incident_invalidated=True,
    )


# ============================================================
# INGEST DRIFT
# ============================================================

@router.post(
    "/ingest/drift",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest drift reconstruction",
)
async def ingest_drift(
    drift: DriftSchema,
) -> IngestionResponse:
    """
    Receive Role 3 drift reconstruction.

    Current DriftSchema does not contain spill_id.

    Therefore the drift result is associated with the currently
    active GIS spill.
    """

    active_spill_id = get_active_spill_id()

    if active_spill_id is None:

        logger.error(
            "Drift handoff rejected: no active spill."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No spill data has been ingested yet. "
                "Submit /api/ingest/spill before drift data."
            ),
        )

    logger.info(
        "Drift handoff received | spill_id=%s | "
        "uncertainty_radius=%.2f km",
        active_spill_id,
        drift.uncertainty_radius_km,
    )

    pipeline_inputs.drift = drift

    invalidate_previous_incident(
        active_spill_id
    )

    logger.info(
        "Drift data stored successfully | spill_id=%s",
        active_spill_id,
    )

    return IngestionResponse(
        status="success",
        message="Drift data ingested successfully.",
        spill_id=active_spill_id,
        cached_incident_invalidated=True,
    )


# ============================================================
# INGEST AIS VESSELS
# ============================================================

@router.post(
    "/ingest/vessels",
    response_model=VesselIngestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest AIS candidate vessels",
)
async def ingest_vessels(
    vessels: List[VesselSchema],
) -> VesselIngestionResponse:
    """
    Receive cleaned Role 4 AIS candidates.

    The request must contain a JSON array.

    All vessels must belong to the same spill.
    """

    if not vessels:

        logger.error(
            "AIS handoff rejected: empty candidate list."
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "At least one candidate vessel is required."
            ),
        )

    spill_id = vessels[0].spill_id

    # Ensure all vessels belong to the same incident.
    for vessel in vessels:

        if vessel.spill_id != spill_id:

            logger.error(
                "AIS handoff rejected: mixed spill IDs."
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "All candidate vessels must belong "
                    "to the same spill_id."
                ),
            )

    # If GIS data already exists, enforce consistency.
    active_spill_id = get_active_spill_id()

    if active_spill_id is not None:

        validate_same_spill_id(
            expected_spill_id=active_spill_id,
            actual_spill_id=spill_id,
            source="AIS",
        )

    logger.info(
        "AIS handoff received | spill_id=%s | "
        "candidate_count=%d",
        spill_id,
        len(vessels),
    )

    pipeline_inputs.vessels = vessels
    state_manager.save_vessels(vessels)

    invalidate_previous_incident(
        spill_id
    )

    logger.info(
        "AIS candidates stored successfully | "
        "spill_id=%s | count=%d",
        spill_id,
        len(vessels),
    )

    return VesselIngestionResponse(
        status="success",
        message=(
            "AIS candidate vessels ingested successfully."
        ),
        spill_id=spill_id,
        vessel_count=len(vessels),
        cached_incident_invalidated=True,
    )


# ============================================================
# RUN PIPELINE
# ============================================================

@router.post(
    "/run-pipeline",
    response_model=PipelineRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run TRACE attribution pipeline",
)
async def run_pipeline() -> PipelineRunResponse:
    """
    Execute the complete TRACE attribution pipeline.

    Required inputs:

        1. GIS spill
        2. Drift reconstruction
        3. AIS candidate vessels

    Processing:

        upstream inputs
             ↓
        attribution engine
             ↓
        ranked candidates
             ↓
        MasterIncidentResponse
             ↓
        IncidentStateManager
             ↓
        memory + JSON persistence
    """

    logger.info(
        "Pipeline execution requested."
    )

    # ========================================================
    # VALIDATE GIS
    # ========================================================

    if pipeline_inputs.spill is None:

        logger.error(
            "Pipeline failed: GIS spill missing."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot run pipeline: GIS spill data "
                "has not been ingested."
            ),
        )

    # ========================================================
    # VALIDATE DRIFT
    # ========================================================

    if pipeline_inputs.drift is None:

        logger.error(
            "Pipeline failed: drift data missing."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot run pipeline: drift data "
                "has not been ingested."
            ),
        )

    # ========================================================
    # VALIDATE AIS
    # ========================================================

    if not pipeline_inputs.vessels:

        logger.error(
            "Pipeline failed: AIS candidates missing."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot run pipeline: AIS candidate vessels "
                "have not been ingested."
            ),
        )

    # ========================================================
    # RETRIEVE INPUTS
    # ========================================================

    spill = pipeline_inputs.spill

    drift = pipeline_inputs.drift

    vessels = pipeline_inputs.vessels

    logger.info(
        "All upstream inputs available | "
        "spill=%s | vessels=%d",
        spill.spill_id,
        len(vessels),
    )

    # ========================================================
    # VALIDATE AIS SPILL IDs
    # ========================================================

    for vessel in vessels:

        validate_same_spill_id(
            expected_spill_id=spill.spill_id,
            actual_spill_id=vessel.spill_id,
            source="AIS",
        )

    # ========================================================
    # RUN ATTRIBUTION ENGINE
    # ========================================================

    logger.info(
        "Starting attribution engine | spill_id=%s",
        spill.spill_id,
    )

    try:

        ranked_candidates = rank_vessels(
            vessels=vessels,
            spill=spill,
            drift=drift,
        )

    except Exception as exc:

        logger.exception(
            "Attribution engine failed | spill_id=%s",
            spill.spill_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Attribution engine failed while processing "
                "the candidate vessels."
            ),
        ) from exc

    # ========================================================
    # BUILD UNIFIED INCIDENT
    # ========================================================

    generation_time = datetime.now(
        timezone.utc
    )

    incident = MasterIncidentResponse(
        incident_id=spill.spill_id,

        spill=spill,

        drift=drift,

        ranked_candidates=ranked_candidates,

        metadata={
            "generation_timestamp": generation_time,
            "system_version": "TRACE-0.2.0",
        },
    )

    # ========================================================
    # SAVE INCIDENT
    # ========================================================

    try:

        state_manager.save_incident(
            incident
        )

    except RuntimeError as exc:

        logger.exception(
            "Incident persistence failed | spill_id=%s",
            spill.spill_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Pipeline completed, but the consolidated "
                "incident could not be saved."
            ),
        ) from exc

    # ========================================================
    # LOG SUCCESS
    # ========================================================

    top_candidate = (
        ranked_candidates[0]
        if ranked_candidates
        else None
    )

    logger.info(
        "Pipeline completed successfully | "
        "incident_id=%s | candidates=%d | "
        "top_candidate=%s",
        incident.incident_id,
        len(ranked_candidates),
        (
            top_candidate.vessel_identity
            if top_candidate
            else "None"
        ),
    )

    # ========================================================
    # RETURN
    # ========================================================

    return PipelineRunResponse(
        status="success",

        message=(
            "TRACE pipeline executed successfully "
            "and incident state saved."
        ),

        incident_id=incident.incident_id,

        candidate_count=len(
            ranked_candidates
        ),

        top_candidate=top_candidate,

        incident=incident,
    )


# ============================================================
# GET LATEST INCIDENT
# ============================================================

@router.get(
    "/incident",
    response_model=MasterIncidentResponse,
    summary="Get latest unified incident",
)
async def get_latest_incident() -> MasterIncidentResponse:
    """
    Return the latest incident.

    In offline demo mode, automatically fall back to the
    static mock incident when no live incident exists.
    """

    incident = state_manager.get_latest_incident()

    # --------------------------------------------------------
    # LIVE STATE AVAILABLE
    # --------------------------------------------------------

    if incident is not None:

        logger.info(
            "Returning live incident | spill_id=%s",
            incident.spill.spill_id,
        )

        return incident

    # --------------------------------------------------------
    # OFFLINE DEMO FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "No live incident available. "
            "USE_MOCK_DATA=true -> using mock incident."
        )

        from app.mock_data import MOCK_INCIDENT

        return MOCK_INCIDENT

    # --------------------------------------------------------
    # LIVE MODE WITH NO DATA
    # --------------------------------------------------------

    raise PipelineStateError(
        "No active incident is available. "
        "Ingest GIS, Drift, and AIS data and run "
        "/api/run-pipeline."
    )

# ============================================================
# GET INCIDENT BY SPILL ID
# ============================================================

@router.get(
    "/incident/{spill_id}",
    response_model=MasterIncidentResponse,
    summary="Get incident by spill ID",
)
async def get_incident_by_spill_id(
    spill_id: str,
) -> MasterIncidentResponse:
    """
    Retrieve a specific persisted investigation session.
    """

    incident = state_manager.get_incident(
        spill_id
    )

    if incident is None:

        logger.warning(
            "Incident not found | spill_id=%s",
            spill_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Incident '{spill_id}' was not found."
            ),
        )

    return incident


# ============================================================
# GET PIPELINE RESULT
# ============================================================

@router.get(
    "/pipeline-result",
    response_model=MasterIncidentResponse,
    summary="Get latest pipeline result",
)
async def get_pipeline_result() -> MasterIncidentResponse:
    """
    Return the latest persisted pipeline result.

    This is effectively an alias for the latest incident
    endpoint and is useful for debugging/demo purposes.
    """

    incident = (
        state_manager.get_latest_incident()
    )

    if incident is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No pipeline result is currently available. "
                "Run /api/run-pipeline first."
            ),
        )

    return incident


# ============================================================
# DELETE ONE INCIDENT
# ============================================================

@router.delete(
    "/incident/{spill_id}",
    summary="Clear an incident session",
)
async def delete_incident(
    spill_id: str,
):
    """
    Delete one investigation session.

    Useful for starting a new demo scenario.
    """

    deleted = state_manager.clear_incident(
        spill_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Incident '{spill_id}' was not found."
            ),
        )

    return {
        "status": "success",
        "message": (
            f"Incident '{spill_id}' cleared successfully."
        ),
        "spill_id": spill_id,
    }


# ============================================================
# DELETE ALL INCIDENTS
# ============================================================

@router.delete(
    "/incidents",
    summary="Reset all incident sessions",
)
async def reset_all_incidents():
    """
    Clear every persisted investigation session.

    Useful for resetting the SIH demo.
    """

    deleted_count = (
        state_manager.clear_all()
    )

    return {
        "status": "success",
        "message": (
            "All incident sessions cleared."
        ),
        "deleted_count": deleted_count,
    }