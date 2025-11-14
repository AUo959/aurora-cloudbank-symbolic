"""Base classes for Opal2 components.

Each component exposes a common interface so that the :class:`Opal2Core`
can orchestrate them interchangeably.  Components may optionally implement
``initialize`` and ``shutdown`` hooks for setup and teardown logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List
import logging


class Opal2Component(ABC):
    """Abstract base class for pluggable Opal2 modules."""
    #: Unique identifier used when registering the component with the core
    name: str = "component"
    #: Optional human readable description of the module
    description: str = ""
    #: List of high-level capabilities supported by the component
    capabilities: List[str] = []

    log: logging.Logger

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process ``data`` and return a result."""
        raise NotImplementedError

    def validate(self, output: Any) -> bool:
        """Validate ``output`` produced by :meth:`process`.

        Components may override this to perform consistency checks.  The
        default implementation simply returns ``True``.
        """
        return True

    def initialize(self) -> None:  # pragma: no cover - simple default
        """Optional initialization hook."""
        pass

    def shutdown(self) -> None:  # pragma: no cover - simple default
        """Optional shutdown hook."""
        pass
