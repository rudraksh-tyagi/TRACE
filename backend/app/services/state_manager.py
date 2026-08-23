"""
TRACE - Incident State Management Service

Phase 2 - Part 3

Provides lightweight incident/session storage for the TRACE
prototype.

Storage strategy:

    1. In-memory dictionary for fast access.
    2. Local JSON persistence for demo/restart resilience.

The service stores the final unified MasterIncidentResponse.

Example:

    incidents/
        SP001.json
        SP002.json

This is intentionally lightweight for the SIH prototype.
A database can replace this service later without changing
the API layer.
"""

import json
import logging
from pathlib import Path
from threading import RLock
from typing import Dict, List, Optional

from app.schemas.schemas import MasterIncidentResponse


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("trace.state_manager")


# ============================================================
# STORAGE LOCATION
# ============================================================

# backend/incidents/
BASE_DIR = Path(__file__).resolve().parents[2]

INCIDENTS_DIR = BASE_DIR / "incidents"

INCIDENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# STATE MANAGER
# ============================================================


class IncidentStateManager:
    """
    Manage active TRACE investigation sessions.

    Data is kept in memory and persisted as JSON.

    The dictionary provides fast access during the running
    application.

    JSON files provide lightweight persistence across a server
    restart.
    """

    def __init__(
        self,
        storage_dir: Path = INCIDENTS_DIR,
    ) -> None:

        self.storage_dir = Path(
            storage_dir
        )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._latest_vessels = []
        self._incidents: Dict[
            str,
            MasterIncidentResponse,
        ] = {}

        self._lock = RLock()

        logger.info(
            "Incident state manager initialized | path=%s",
            self.storage_dir,
        )

        self._load_existing_incidents()

    # ========================================================
    # FILE HELPERS
    # ========================================================

    def _get_file_path(
        self,
        spill_id: str,
    ) -> Path:
        """
        Return JSON file path for a spill.

        Spill IDs are restricted to a safe filename format.
        """

        safe_spill_id = "".join(
            character
            for character in spill_id
            if character.isalnum()
            or character in ("-", "_")
        )

        if not safe_spill_id:

            raise ValueError(
                "Invalid spill_id."
            )

        return (
            self.storage_dir
            / f"{safe_spill_id}.json"
        )

    # ========================================================
    # LOAD
    # ========================================================

    def _load_existing_incidents(self) -> None:
        """
        Load previously persisted incidents into memory.

        A corrupted individual JSON file does not prevent the
        remaining incidents from loading.
        """

        files = self.storage_dir.glob(
            "*.json"
        )

        for file_path in files:

            try:

                with file_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    payload = json.load(file)

                incident = (
                    MasterIncidentResponse.model_validate(
                        payload
                    )
                )

                self._incidents[
                    incident.spill.spill_id
                ] = incident

                logger.info(
                    "Loaded incident from disk | spill_id=%s",
                    incident.spill.spill_id,
                )

            except (
                OSError,
                json.JSONDecodeError,
                ValueError,
            ) as exc:

                logger.error(
                    "Could not load incident file %s: %s",
                    file_path,
                    exc,
                )

    # ========================================================
    # SAVE / UPDATE
    # ========================================================

    def save_incident(
        self,
        incident: MasterIncidentResponse,
    ) -> MasterIncidentResponse:
        """
        Save or update an incident session.

        The spill_id is used as the primary session key.
        """

        spill_id = incident.spill.spill_id

        if not spill_id:

            raise ValueError(
                "Incident must contain a spill_id."
            )

        file_path = self._get_file_path(
            spill_id
        )

        with self._lock:

            # ----------------------------------------------
            # Memory
            # ----------------------------------------------

            self._incidents[
                spill_id
            ] = incident

            # ----------------------------------------------
            # JSON persistence
            # ----------------------------------------------

            try:

                with file_path.open(
                    "w",
                    encoding="utf-8",
                ) as file:

                    json.dump(
                        incident.model_dump(
                            mode="json"
                        ),
                        file,
                        indent=2,
                        ensure_ascii=False,
                    )

            except OSError as exc:

                logger.exception(
                    "Failed to persist incident | spill_id=%s",
                    spill_id,
                )

                raise RuntimeError(
                    f"Could not persist incident "
                    f"{spill_id}."
                ) from exc

        logger.info(
            "Incident saved | spill_id=%s",
            spill_id,
        )

        return incident

    # ========================================================
    # RETRIEVE
    # ========================================================

    def get_incident(
        self,
        spill_id: str,
    ) -> Optional[MasterIncidentResponse]:
        """
        Retrieve an incident by spill_id.

        Returns:
            MasterIncidentResponse if found.
            None if not found.
        """

        with self._lock:

            incident = self._incidents.get(
                spill_id
            )

            if incident is not None:
                return incident

        # ----------------------------------------------------
        # Fallback to disk in case it exists but isn't loaded.
        # ----------------------------------------------------

        file_path = self._get_file_path(
            spill_id
        )

        if not file_path.exists():
            return None

        try:

            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                payload = json.load(file)

            incident = (
                MasterIncidentResponse.model_validate(
                    payload
                )
            )

            with self._lock:

                self._incidents[
                    spill_id
                ] = incident

            return incident

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:

            logger.error(
                "Failed to retrieve incident %s: %s",
                spill_id,
                exc,
            )

            return None

    # ========================================================
    # LATEST INCIDENT
    # ========================================================

    def get_latest_incident(
        self,
    ) -> Optional[MasterIncidentResponse]:
        """
        Return the most recently generated incident.

        Generation timestamp is used for ordering.
        """

        with self._lock:

            if not self._incidents:
                return None

            return max(
                self._incidents.values(),
                key=lambda incident: (
                    incident.metadata
                    .generation_timestamp
                ),
            )

    # ========================================================
    # LIST INCIDENTS
    # ========================================================

    def list_incidents(
        self,
    ) -> List[MasterIncidentResponse]:
        """
        Return all stored incidents.
        """

        with self._lock:

            return list(
                self._incidents.values()
            )

    # ========================================================
    # DELETE / RESET
    # ========================================================

    def clear_incident(
        self,
        spill_id: str,
    ) -> bool:
        """
        Delete an incident from memory and disk.

        Returns:
            True if an incident existed.
            False if nothing was found.
        """

        file_path = self._get_file_path(
            spill_id
        )

        with self._lock:

            existed = (
                spill_id
                in self._incidents
            )

            self._incidents.pop(
                spill_id,
                None,
            )

            if file_path.exists():

                try:

                    file_path.unlink()

                    existed = True

                except OSError as exc:

                    logger.error(
                        "Failed to delete incident file "
                        "%s: %s",
                        file_path,
                        exc,
                    )

                    raise RuntimeError(
                        f"Could not delete incident "
                        f"{spill_id}."
                    ) from exc

        logger.info(
            "Incident cleared | spill_id=%s",
            spill_id,
        )

        return existed

    # ========================================================
    # CLEAR EVERYTHING
    # ========================================================

    def clear_all(
        self,
    ) -> int:
        """
        Clear all stored incidents.

        Useful for starting a fresh SIH demo scenario.

        Returns:
            Number of incidents removed.
        """

        with self._lock:

            incident_count = len(
                self._incidents
            )

            self._incidents.clear()

            for file_path in self.storage_dir.glob(
                "*.json"
            ):

                try:

                    file_path.unlink()

                except OSError as exc:

                    logger.error(
                        "Could not delete %s: %s",
                        file_path,
                        exc,
                    )

        logger.info(
            "All incidents cleared | count=%d",
            incident_count,
        )

        return incident_count

    # ========================================================
    # STATUS
    # ========================================================

    def has_incident(
        self,
        spill_id: str,
    ) -> bool:
        """Check whether an incident exists."""

        return (
            self.get_incident(
                spill_id
            )
            is not None
        )


# ============================================================
# APPLICATION-WIDE INSTANCE
# ============================================================


    def save_vessels(self, vessels):
        """
        Store the latest ingested AIS vessel list.
        """
        self._latest_vessels = vessels


    def get_vessels(self):
        """
        Return the latest stored AIS vessel list.
        """
        return self._latest_vessels

state_manager = IncidentStateManager()