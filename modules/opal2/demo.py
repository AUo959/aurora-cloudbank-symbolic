"""Small demonstration of the Opal2 core and plugin modules."""
from __future__ import annotations

from .opal2_core import Opal2Core
from .regex_engine import RegexGenerationEngine
from .symbolic_logic import SymbolicLogicEngine
from .ethics_governor import EthicsGovernor


def main() -> None:
    core = Opal2Core()
    core.register_component(RegexGenerationEngine())
    core.register_component(SymbolicLogicEngine())
    core.register_component(EthicsGovernor())

    print("Available components:", core.available_components())

    regex = core.use_components(["regex", "ethics"], "email")
    result = core.run_capability("symbolic_processing", "2 + 2")
    print("Generated regex:", regex)
    print("Symbolic logic result:", result)

    # Using another description
    seq_regex = core.use_components(["regex"], "exactly 5 digits")
    print("Regex for exactly 5 digits:", seq_regex)

    # Generate regex from examples
    ex_regex = core.use_components([
        "regex"
    ], {"examples": ["abc123end", "abc999end"]})
    print("Regex from examples:", ex_regex)


if __name__ == "__main__":  # pragma: no cover - manual demo
    main()
