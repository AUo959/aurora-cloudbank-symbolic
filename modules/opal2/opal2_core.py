"""Central orchestrator for Opal2 components."""
from __future__ import annotations

from typing import Any, Dict, List
import logging

from .base_component import Opal2Component


class Opal2Core:
    """Manage and run Opal2 components."""

    def __init__(self) -> None:
        self.components: Dict[str, Opal2Component] = {}
        self.log = logging.getLogger(self.__class__.__name__)

    def register_component(self, component: Opal2Component) -> None:
        """Add ``component`` to the registry."""
        component.initialize()
        self.components[component.name] = component
        self.log.debug("Registered component %s", component.name)

    def unregister_component(self, name: str) -> None:
        comp = self.components.pop(name, None)
        if comp is not None:
            comp.shutdown()
            self.log.debug("Unregistered component %s", name)

    def use_components(self, names: List[str], data: Any) -> Any:
        """Pass ``data`` through the named components sequentially."""
        output = data
        for name in names:
            comp = self.components.get(name)
            if comp is None:
                raise ValueError(f"Component '{name}' not registered")
            try:
                self.log.debug("Running component %s", name)
                output = comp.process(output)
                if not comp.validate(output):
                    raise ValueError(f"Component '{name}' validation failed")
            except Exception as exc:  # pragma: no cover - simple error path
                raise RuntimeError(f"Component '{name}' failed: {exc}") from exc
        return output

    def run_capability(self, capability: str, data: Any) -> Any:
        """Run the first component supporting ``capability`` on ``data``."""
        for comp in self.components.values():
            if capability in getattr(comp, "capabilities", []):
                return self.use_components([comp.name], data)
        raise ValueError(f"No component with capability '{capability}' registered")

    def available_components(self) -> List[str]:
        return sorted(self.components)
