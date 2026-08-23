"""
TRACE Phase 3 Part 3
End-to-End Integration and Payload Testing.
"""

import sys
from typing import Any

import requests

from app.schemas.schemas import (
    AttributionSchema,
    DriftSchema,
    MasterIncidentResponse,
    SpillSchema,
    VesselSchema,
)


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10


def get(path: str) -> requests.Response:
    """Send a GET request to the TRACE backend."""

    url = f"{BASE_URL}{path}"

    print(f"\nGET {path}")

    try:
        response = requests.get(
            url,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"Connection failed: {exc}")
        sys.exit(1)

    print(f"Status: {response.status_code}")

    return response


def check_status(
    response: requests.Response,
    expected: int = 200,
) -> None:
    """Verify HTTP status."""

    if response.status_code != expected:
        print(
            f"Expected {expected}, "
            f"received {response.status_code}"
        )

        try:
            print(response.json())
        except ValueError:
            print(response.text)

        sys.exit(1)

    print(f"HTTP {expected} OK")


def get_json(
    response: requests.Response,
) -> Any:
    """Verify that the response is JSON."""

    try:
        payload = response.json()
    except ValueError:
        print("Response is not valid JSON.")
        sys.exit(1)

    print("Valid JSON")
    return payload


# ============================================================
# HEALTH
# ============================================================

def test_health() -> None:

    response = get("/health")

    check_status(response)

    payload = get_json(response)

    assert payload["status"] == "healthy"

    print("Health check passed")


# ============================================================
# SPILL
# ============================================================

def test_spill() -> None:

    response = get("/api/spill")

    check_status(response)

    payload = get_json(response)

    try:
        spill = SpillSchema.model_validate(payload)
    except Exception as exc:
        print("Spill schema validation failed:")
        print(exc)
        sys.exit(1)

    print(
        f"Spill schema valid | "
        f"spill_id={spill.spill_id}"
    )


# ============================================================
# DRIFT
# ============================================================

def test_drift() -> None:

    response = get("/api/drift")

    check_status(response)

    payload = get_json(response)

    try:
        drift = DriftSchema.model_validate(payload)
    except Exception as exc:
        print("Drift schema validation failed:")
        print(exc)
        sys.exit(1)

    print(
        "Drift schema valid | "
        f"backward_points={len(drift.backward_track)} | "
        f"forecast_tracks={len(drift.forecast_tracks)}"
    )


# ============================================================
# VESSELS
# ============================================================

def test_vessels() -> None:

    response = get("/api/vessels")

    check_status(response)

    payload = get_json(response)

    if not isinstance(payload, list):
        print("/api/vessels did not return a list.")
        sys.exit(1)

    for index, vessel_payload in enumerate(
        payload,
        start=1,
    ):
        try:
            VesselSchema.model_validate(
                vessel_payload
            )
        except Exception as exc:
            print(
                f"Vessel #{index} schema validation failed:"
            )
            print(exc)
            sys.exit(1)

    print(
        f"Vessel schema validation passed | "
        f"count={len(payload)}"
    )


# ============================================================
# ATTRIBUTION
# ============================================================

def test_attribution() -> None:

    response = get("/api/attribution")

    check_status(response)

    payload = get_json(response)

    if not isinstance(payload, list):
        print(
            "/api/attribution did not return a list."
        )
        sys.exit(1)

    candidates = []

    for index, candidate_payload in enumerate(
        payload,
        start=1,
    ):
        try:
            candidate = (
                AttributionSchema.model_validate(
                    candidate_payload
                )
            )
        except Exception as exc:
            print(
                f"Attribution #{index} "
                "schema validation failed:"
            )
            print(exc)
            sys.exit(1)

        candidates.append(candidate)

    print(
        f"Attribution schema validation passed | "
        f"count={len(candidates)}"
    )

    scores = [
        candidate.overall_score
        for candidate in candidates
    ]

    if scores != sorted(
        scores,
        reverse=True,
    ):
        print(
            "Attribution candidates are not "
            "sorted by descending score."
        )
        sys.exit(1)

    print("Attribution ranking order valid")


# ============================================================
# INCIDENT
# ============================================================

def test_incident() -> None:

    response = get("/api/incident")

    check_status(response)

    payload = get_json(response)

    try:
        incident = (
            MasterIncidentResponse.model_validate(
                payload
            )
        )
    except Exception as exc:
        print(
            "Incident schema validation failed:"
        )
        print(exc)
        sys.exit(1)

    print(
        f"Incident schema valid | "
        f"incident_id={incident.incident_id}"
    )


# ============================================================
# COMPLETE INCIDENT
# ============================================================

def test_complete_incident() -> None:

    response = get("/api/incident/complete")

    check_status(response)

    payload = get_json(response)

    try:
        incident = (
            MasterIncidentResponse.model_validate(
                payload
            )
        )
    except Exception as exc:
        print(
            "Complete incident schema "
            "validation failed:"
        )
        print(exc)
        sys.exit(1)

    assert incident.incident_id
    assert incident.spill is not None
    assert incident.drift is not None
    assert incident.ranked_candidates is not None
    assert incident.metadata is not None

    print(
        "Complete incident schema valid"
    )

    print(
        f"Incident ID: {incident.incident_id}"
    )

    print(
        f"Spill ID: {incident.spill.spill_id}"
    )

    print(
        f"Candidate count: "
        f"{len(incident.ranked_candidates)}"
    )

    scores = [
        candidate.overall_score
        for candidate in incident.ranked_candidates
    ]

    if scores != sorted(
        scores,
        reverse=True,
    ):
        print(
            "Complete incident candidates "
            "are not correctly ranked."
        )
        sys.exit(1)

    print(
        "Complete incident ranking valid"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print(
        "\n"
        "==================================================\n"
        "TRACE PHASE 3 PART 3\n"
        "END-TO-END INTEGRATION TEST\n"
        "=================================================="
    )

    test_health()
    test_spill()
    test_drift()
    test_vessels()
    test_attribution()
    test_incident()
    test_complete_incident()

    print(
        "\n"
        "==================================================\n"
        "ALL INTEGRATION TESTS PASSED\n"
        "=================================================="
    )


if __name__ == "__main__":
    main()