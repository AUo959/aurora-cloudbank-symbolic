"""DEPRECATED import path — use src.api.l1_relay_api instead.

"L2 Meta-Agent" was a canon error: the relay agents are L1-resident and
only play the Layer 2 verifier ROLE in the Triplex protocol. See
docs/architecture/LAYER_ARCHITECTURE.md.

`router` here is the legacy-prefixed router (/api/l2-agents/*, marked
deprecated in OpenAPI), so any existing `include_router` of this module
keeps serving the exact same paths.
"""

import warnings

from src.api.l1_relay_api import (  # noqa: F401
    canonical_router,
    legacy_router,
)
from src.api.l1_relay_api import legacy_router as router  # noqa: F401

warnings.warn(
    "src.api.l2_meta_agent_api is deprecated; import src.api.l1_relay_api "
    "instead (canonical routes: /api/l1-relay-agents/*)",
    DeprecationWarning,
    stacklevel=2,
)
