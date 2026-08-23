"""
TRACE Phase 2 Part 1
Attribution Engine Test
"""

from app.mock_data import (
    MOCK_DRIFT,
    MOCK_SPILL,
    MOCK_VESSELS,
)

from app.services.attribution_engine import (
    calculate_attribution,
    rank_vessels,
)


print()
print("=" * 60)
print("TRACE - PHASE 2 PART 1")
print("EXPLAINABLE ATTRIBUTION ENGINE TEST")
print("=" * 60)


# ============================================================
# TEST ONE VESSEL
# ============================================================


vessel = MOCK_VESSELS[0]

result = calculate_attribution(
    vessel=vessel,
    spill=MOCK_SPILL,
    drift=MOCK_DRIFT,
)


print()
print("--- SINGLE VESSEL TEST ---")

print(
    f"MMSI:             {result.mmsi}"
)

print(
    f"Vessel:           {result.vessel_identity}"
)

print(
    f"Overall Score:    {result.overall_score}%"
)


print()
print("Component Scores:")

print(
    f"  Distance:       "
    f"{result.component_scores.distance_score}"
)

print(
    f"  Time:           "
    f"{result.component_scores.time_compatibility_score}"
)

print(
    f"  Trajectory:     "
    f"{result.component_scores.trajectory_consistency_score}"
)

print(
    f"  Behavior:       "
    f"{result.component_scores.behavior_score}"
)


print()
print("Explanations:")

for explanation in result.explanations:

    print(
        f"  - {explanation}"
    )


# ============================================================
# TEST ALL VESSELS
# ============================================================


ranked = rank_vessels(
    vessels=MOCK_VESSELS,
    spill=MOCK_SPILL,
    drift=MOCK_DRIFT,
)


print()
print("--- RANKED CANDIDATES ---")


for index, candidate in enumerate(
    ranked,
    start=1,
):

    print(
        f"{index}. "
        f"{candidate.vessel_identity} "
        f"({candidate.mmsi}) "
        f"-> {candidate.overall_score}%"
    )


# ============================================================
# ASSERTIONS
# ============================================================


assert result.overall_score >= 0.0

assert result.overall_score <= 100.0

assert len(
    result.explanations
) > 0

assert len(
    ranked
) == len(
    MOCK_VESSELS
)


# Verify descending order.

for index in range(
    len(ranked) - 1
):

    assert (
        ranked[index].overall_score
        >=
        ranked[index + 1].overall_score
    )


# Verify Pydantic output.

assert result.mmsi == vessel.mmsi

assert (
    result.vessel_identity
    == vessel.vessel_name
)


print()
print("=" * 60)
print("✅ ALL PHASE 2 PART 1 TESTS PASSED")
print("=" * 60)
print()