"""
TRACE - Explainable Vessel Attribution Engine

Phase 2 - Part 1

Deterministic scoring engine.

Weights:

    Distance       35%
    Time           25%
    Trajectory     25%
    Behavior       15%

Total             100%

No machine learning is used in this prototype.
"""

from math import asin, cos, radians, sin, sqrt
from typing import List, Tuple

from app.schemas.schemas import (
    AttributionSchema,
    ComponentScores,
    DriftSchema,
    SpillSchema,
    VesselSchema,
)


# ============================================================
# CONFIGURATION
# ============================================================

DISTANCE_WEIGHT = 0.35
TIME_WEIGHT = 0.25
TRAJECTORY_WEIGHT = 0.25
BEHAVIOR_WEIGHT = 0.15

MAX_RELEVANT_DISTANCE_KM = 10.0


# ============================================================
# HAVERSINE
# ============================================================


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate great-circle distance in kilometres."""

    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    c = 2 * asin(sqrt(a))

    return earth_radius_km * c


# ============================================================
# DISTANCE SCORE
# ============================================================


def calculate_distance_score(
    vessel: VesselSchema,
) -> Tuple[float, float]:
    """
    Convert minimum distance into a 0-100 score.

    0 km  -> 100
    5 km  -> 50
    10 km -> 0
    """

    distance = vessel.minimum_distance_km

    if MAX_RELEVANT_DISTANCE_KM <= 0:
        return 0.0, distance

    if distance >= MAX_RELEVANT_DISTANCE_KM:
        return 0.0, distance

    score = (
        1.0
        - distance / MAX_RELEVANT_DISTANCE_KM
    ) * 100.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    ), distance


# ============================================================
# TIME SCORE
# ============================================================


def calculate_time_score(
    vessel: VesselSchema,
) -> float:
    """
    Calculate time compatibility.

    Presence during source window gives a base score of 70.

    Additional time spent near source contributes up to
    another 30 points.

    60+ minutes near source = maximum bonus.
    """

    if not vessel.source_window_presence:
        return 0.0

    base_score = 70.0

    time_bonus = min(
        vessel.time_spent_near_source_min / 60.0,
        1.0,
    ) * 30.0

    return round(
        min(100.0, base_score + time_bonus),
        2,
    )


# ============================================================
# TRAJECTORY SCORE
# ============================================================


def calculate_trajectory_score(
    vessel: VesselSchema,
    drift: DriftSchema,
) -> float:
    """
    Compare vessel trajectory against reconstructed drift.

    For every AIS point:

        Find nearest drift point
        ↓
        Convert distance to score
        ↓
        Average all point scores
    """

    if not vessel.trajectory:
        return 0.0

    drift_points = list(
        drift.backward_track
    )

    for forecast_track in drift.forecast_tracks:
        drift_points.extend(
            forecast_track.points
        )

    if not drift_points:
        return 0.0

    point_scores = []

    for vessel_point in vessel.trajectory:

        nearest_distance = min(
            haversine_distance_km(
                vessel_point.lat,
                vessel_point.lon,
                drift_point.lat,
                drift_point.lon,
            )
            for drift_point in drift_points
        )

        if nearest_distance >= MAX_RELEVANT_DISTANCE_KM:

            point_score = 0.0

        else:

            point_score = (
                1.0
                - nearest_distance
                / MAX_RELEVANT_DISTANCE_KM
            ) * 100.0

        point_scores.append(point_score)

    if not point_scores:
        return 0.0

    return round(
        sum(point_scores) / len(point_scores),
        2,
    )


# ============================================================
# BEHAVIOR SCORE
# ============================================================


def calculate_behavior_score(
    vessel: VesselSchema,
) -> Tuple[float, List[str]]:
    """
    Calculate behavior score from the current Role 4 contract.

    Current behavioral indicator:

        ais_gap_detected
    """

    if vessel.ais_gap_detected:

        return 100.0, [
            "AIS transponder gap greater than 60 minutes "
            "was detected near the source."
        ]

    return 0.0, [
        "No significant AIS gap was detected near the source."
    ]


# ============================================================
# OVERALL SCORE
# ============================================================


def calculate_overall_score(
    components: ComponentScores,
) -> float:
    """Calculate weighted overall attribution score."""

    score = (
        components.distance_score
        * DISTANCE_WEIGHT

        + components.time_compatibility_score
        * TIME_WEIGHT

        + components.trajectory_consistency_score
        * TRAJECTORY_WEIGHT

        + components.behavior_score
        * BEHAVIOR_WEIGHT
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# EXPLANATIONS
# ============================================================


def generate_explanations(
    vessel: VesselSchema,
    distance_km: float,
    distance_score: float,
    time_score: float,
    trajectory_score: float,
    behavior_explanations: List[str],
) -> List[str]:
    """Generate human-readable evidence."""

    explanations: List[str] = []

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    explanations.append(
        f"Vessel passed approximately "
        f"{distance_km:.2f} km from the estimated spill origin."
    )

    if distance_score >= 80:

        explanations.append(
            "Vessel was in very close proximity to the "
            "estimated spill source."
        )

    elif distance_score >= 50:

        explanations.append(
            "Vessel was within the relevant proximity range "
            "of the estimated spill source."
        )

    else:

        explanations.append(
            "Vessel was relatively far from the estimated "
            "spill source."
        )

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    if vessel.source_window_presence:

        explanations.append(
            "Vessel was present during the estimated "
            "source time window."
        )

        explanations.append(
            f"Vessel spent approximately "
            f"{vessel.time_spent_near_source_min} minutes "
            f"near the estimated source."
        )

    else:

        explanations.append(
            "Vessel was not confirmed during the estimated "
            "source time window."
        )

    # --------------------------------------------------------
    # Trajectory
    # --------------------------------------------------------

    if trajectory_score >= 75:

        explanations.append(
            "Vessel trajectory is strongly consistent with "
            "the reconstructed spill drift."
        )

    elif trajectory_score >= 50:

        explanations.append(
            "Vessel trajectory shows moderate consistency "
            "with the reconstructed spill drift."
        )

    elif trajectory_score > 0:

        explanations.append(
            "Vessel trajectory shows limited consistency "
            "with the reconstructed spill drift."
        )

    else:

        explanations.append(
            "Insufficient trajectory evidence was available."
        )

    # --------------------------------------------------------
    # Behavior
    # --------------------------------------------------------

    explanations.extend(
        behavior_explanations
    )

    return explanations


# ============================================================
# SINGLE VESSEL
# ============================================================


def calculate_attribution(
    vessel: VesselSchema,
    spill: SpillSchema,
    drift: DriftSchema,
) -> AttributionSchema:
    """
    Calculate explainable attribution for one vessel.
    """

    if vessel is None:
        raise ValueError(
            "Vessel data cannot be None."
        )

    if spill is None:
        raise ValueError(
            "Spill data cannot be None."
        )

    if drift is None:
        raise ValueError(
            "Drift data cannot be None."
        )

    distance_score, distance_km = (
        calculate_distance_score(vessel)
    )

    time_score = calculate_time_score(
        vessel
    )

    trajectory_score = (
        calculate_trajectory_score(
            vessel,
            drift,
        )
    )

    behavior_score, behavior_explanations = (
        calculate_behavior_score(
            vessel
        )
    )

    components = ComponentScores(
        distance_score=distance_score,

        time_compatibility_score=time_score,

        trajectory_consistency_score=trajectory_score,

        behavior_score=behavior_score,
    )

    overall_score = calculate_overall_score(
        components
    )

    explanations = generate_explanations(
        vessel=vessel,
        distance_km=distance_km,
        distance_score=distance_score,
        time_score=time_score,
        trajectory_score=trajectory_score,
        behavior_explanations=behavior_explanations,
    )

    return AttributionSchema(
        mmsi=vessel.mmsi,

        vessel_identity=vessel.vessel_name,

        overall_score=overall_score,

        component_scores=components,

        explanations=explanations,
    )


# ============================================================
# RANK ALL VESSELS
# ============================================================


def rank_vessels(
    vessels: List[VesselSchema],
    spill: SpillSchema,
    drift: DriftSchema,
) -> List[AttributionSchema]:
    """
    Calculate attribution for every candidate and rank them.

    Highest score appears first.
    """

    if not vessels:
        return []

    results: List[AttributionSchema] = []

    for vessel in vessels:

        try:

            result = calculate_attribution(
                vessel=vessel,
                spill=spill,
                drift=drift,
            )

            results.append(result)

        except (
            ValueError,
            TypeError,
            ZeroDivisionError,
        ):
            # One bad candidate should not break the
            # entire attribution pipeline.
            continue

    results.sort(
        key=lambda result: result.overall_score,
        reverse=True,
    )

    return results