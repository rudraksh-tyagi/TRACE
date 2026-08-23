"""
TRACE - Mock / Read API

Phase 3
Offline Demo Mode + Live State Fallback

Behavior:

    USE_MOCK_DATA=true
        Live state available
            -> return live data

        Live state unavailable
            -> return mock data

    USE_MOCK_DATA=false
        Live state available
            -> return live data

        Live state unavailable
            -> return 409 error
"""

import logging

from fastapi import APIRouter

from app.config.settings import settings
from app.exceptions import PipelineStateError
from app.schemas.schemas import MasterIncidentResponse
from app.services.pipeline_orchestrator import execute_full_pipeline
from app.schemas.schemas import (
    AttributionSchema,
    DriftSchema,
    MasterIncidentResponse,
    SpillSchema,
    VesselSchema,
)
from app.services.state_manager import state_manager


logger = logging.getLogger("trace.mock_api")


router = APIRouter(
    prefix="/api",
    tags=["Mock / Demo Data"],
)


# ============================================================
# SPILL
# ============================================================

@router.get(
    "/spill",
    response_model=SpillSchema,
    summary="Get spill information",
)
async def get_spill() -> SpillSchema:
    """
    Return the latest spill information.

    Priority:

        1. Live persisted incident
        2. Mock data when USE_MOCK_DATA=true
        3. 409 error when live data is unavailable
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    incident = state_manager.get_latest_incident()

    if incident is not None:

        logger.info(
            "Returning live spill data | spill_id=%s",
            incident.spill.spill_id,
        )

        return incident.spill

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "Live spill unavailable. "
            "Falling back to mock spill data."
        )

        from app.mock_data import MOCK_SPILL

        return MOCK_SPILL

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA
    # --------------------------------------------------------

    raise PipelineStateError(
        "No live spill data is available. "
        "Ingest GIS spill data first."
    )


# ============================================================
# DRIFT
# ============================================================

@router.get(
    "/drift",
    response_model=DriftSchema,
    summary="Get drift information",
)
async def get_drift() -> DriftSchema:
    """
    Return the latest drift reconstruction.

    Priority:

        1. Live persisted incident
        2. Mock data when USE_MOCK_DATA=true
        3. 409 error when live data is unavailable
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    incident = state_manager.get_latest_incident()

    if incident is not None:

        logger.info(
            "Returning live drift data | spill_id=%s",
            incident.spill.spill_id,
        )

        return incident.drift

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "Live drift unavailable. "
            "Falling back to mock drift data."
        )

        from app.mock_data import MOCK_DRIFT

        return MOCK_DRIFT

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA
    # --------------------------------------------------------

    raise PipelineStateError(
        "No live drift data is available. "
        "Ingest drift data first."
    )


# ============================================================
# VESSELS
# ============================================================

@router.get(
    "/vessels",
    response_model=list[VesselSchema],
    summary="Get candidate vessels",
)
async def get_vessels() -> list[VesselSchema]:
    """
    Return the latest AIS candidate vessel list.

    Vessel data is stored separately by the state manager
    because MasterIncidentResponse contains attribution
    results rather than the original VesselSchema objects.
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    vessels = state_manager.get_vessels()

    if vessels:

        logger.info(
            "Returning live vessel data | count=%d",
            len(vessels),
        )

        return vessels

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "Live vessel data unavailable. "
            "Falling back to mock vessel data."
        )

        from app.mock_data import MOCK_VESSELS

        return MOCK_VESSELS

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA
    # --------------------------------------------------------

    raise PipelineStateError(
        "No live vessel data is available. "
        "Ingest AIS candidate vessels first."
    )


# ============================================================
# ATTRIBUTION
# ============================================================

@router.get(
    "/attribution",
    response_model=list[AttributionSchema],
    summary="Get vessel attribution scores",
)
async def get_attribution() -> list[AttributionSchema]:
    """
    Return ranked vessel attribution results.

    Priority:

        1. Live persisted incident
        2. Mock attribution data
        3. 409 error
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    incident = state_manager.get_latest_incident()

    if incident is not None:

        logger.info(
            "Returning live attribution results | "
            "candidate_count=%d",
            len(incident.ranked_candidates),
        )

        return incident.ranked_candidates

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "Live attribution unavailable. "
            "Falling back to mock attribution data."
        )
    
        from app.mock_data import MOCK_INCIDENT
    
        return MOCK_INCIDENT.ranked_candidates

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA
    # --------------------------------------------------------

    raise PipelineStateError(
        "No live attribution results are available. "
        "Run the attribution pipeline first."
    )


# ============================================================
# COMPLETE INCIDENT
# ============================================================

@router.get(
    "/incident/complete",
    response_model=MasterIncidentResponse,
    summary="Get complete unified incident",
)
async def get_complete_incident() -> MasterIncidentResponse:
    """
    Return the complete unified TRACE incident.

    This endpoint is intended to be the primary endpoint
    consumed by the frontend dashboard.

    Priority:

        1. Live persisted incident
        2. Mock incident when USE_MOCK_DATA=true
        3. 409 error
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    incident = state_manager.get_latest_incident()

    if incident is not None:

        logger.info(
            "Returning complete live incident | spill_id=%s",
            incident.spill.spill_id,
        )

        return incident

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "Live incident unavailable. "
            "Falling back to MOCK_INCIDENT."
        )

        from app.mock_data import MOCK_INCIDENT

        return MOCK_INCIDENT

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA -> AUTO ORCHESTRATE
    # --------------------------------------------------------

    try:
        logger.info("No active incident stored. Auto-executing full pipeline...")
        return execute_full_pipeline()
    except Exception as exc:
        logger.exception("Auto-orchestration failed in get_complete_incident")
        raise PipelineStateError(
            f"No complete incident is available and pipeline execution failed: {exc}"
        ) from exc


# ============================================================
# INCIDENT
# ============================================================

@router.get(
    "/incident",
    response_model=MasterIncidentResponse,
    summary="Get latest unified incident",
)
async def get_incident() -> MasterIncidentResponse:
    """
    Return the latest unified incident.

    This is kept as the primary frontend-compatible endpoint.
    """

    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    incident = state_manager.get_latest_incident()

    if incident is not None:

        logger.info(
            "Returning latest live incident | spill_id=%s",
            incident.spill.spill_id,
        )

        return incident

    # --------------------------------------------------------
    # MOCK FALLBACK
    # --------------------------------------------------------

    if settings.use_mock_data:

        logger.warning(
            "No live incident available. "
            "Falling back to MOCK_INCIDENT."
        )
    
        from app.mock_data import MOCK_INCIDENT
    
        return MOCK_INCIDENT

    # --------------------------------------------------------
    # LIVE MODE WITHOUT DATA -> AUTO ORCHESTRATE
    # --------------------------------------------------------

    try:
        logger.info("No active incident stored. Auto-executing full pipeline...")
        return execute_full_pipeline()
    except Exception as exc:
        logger.exception("Auto-orchestration failed in get_incident")
        raise PipelineStateError(
            f"No active incident is available and pipeline execution failed: {exc}"
        ) from exc