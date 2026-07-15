"""DEPRECATED import path — use src.bridges.l1_relay_bridge instead.

"L2 Meta-Agent" was a canon error: the relay agents are L1-resident
(Orion Station) and only play the Layer 2 verifier ROLE in the Triplex
protocol. See docs/architecture/LAYER_ARCHITECTURE.md.

This shim keeps existing imports working against the canonical
mesh-backed implementation. It re-exports the same objects — including
the module-level singleton — so `l2_bridge` and `l1_relay_bridge` are
one and the same instance.
"""

import warnings

from src.bridges.l1_relay_bridge import (  # noqa: F401
    L1RelayAgent,
    L1RelayBridge,
    cli,
    l1_relay_bridge,
    main,
)

warnings.warn(
    "src.bridges.l2_meta_agent_bridge is deprecated; import "
    "src.bridges.l1_relay_bridge instead (relay agents are L1-resident — "
    "see docs/architecture/LAYER_ARCHITECTURE.md)",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy names
CustomGptAgent = L1RelayAgent
L2MetaAgentBridge = L1RelayBridge
l2_bridge = l1_relay_bridge
