"""Organizational intelligence (stub).

#761: the rest of the HR routes (StaffingAnalyzer, CharacterGenerator)
ship real implementations alongside this module. OrganizationalIntelligence
was referenced by ``modules/hr_system/api/hr_routes.py`` but never
implemented, so the route silently returned mock data on ImportError.

This stub makes the absence explicit:

  * Importing the class succeeds (the route no longer hits ImportError).
  * Calling any method raises ``NotImplementedError`` with a clear
    message. The route's ``except Exception`` clause then returns the
    mock fallback, which the route now annotates with a ``degraded``
    flag so clients can detect that the response is not from a real
    organizational-intelligence backend.

Anyone implementing the real backend should:
  1. Replace this stub with a class that calls into the actual capacity
     / structure data source.
  2. Add an integration test that exercises ``get_capacity_analysis``
     under both happy-path and missing-dependency scenarios.
  3. Remove the ``degraded`` flag from the route fallback once the
     stub is gone.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class OrganizationalIntelligence:
    """Stub implementation (#761).

    All methods raise NotImplementedError. Importing succeeds so the
    HR route handlers exercise their real code path instead of falling
    through on ImportError, which previously masked the missing
    implementation as a generic mock-data response.
    """

    _STATUS = "stub"

    def __init__(self) -> None:
        # Construction succeeds so the route's `intel = ...()` line
        # doesn't trip a confusing error.
        pass

    def get_capacity_analysis(self, department: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError(
            "OrganizationalIntelligence.get_capacity_analysis is not yet "
            "implemented (#761). The HR route falls through to flagged "
            "mock data; replace this stub with a real backend before "
            "treating the response as authoritative."
        )
