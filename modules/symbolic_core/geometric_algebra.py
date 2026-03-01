# geometric_algebra.py
"""
Geometric Algebra utilities for symbolic and quantum-inspired workflows.
Uses the 'clifford' library for core operations if available, otherwise provides a minimal mock implementation.
"""

import os

try:
    import clifford as cf
except Exception:
    cf = None


class GeometricAlgebra:

    def __init__(self):
        # Clifford can trigger unstable native/JIT code paths on some local runtimes.
        # Keep deterministic behavior by defaulting to the mock backend unless explicitly enabled.
        use_clifford = cf is not None and os.getenv("AURORA_ENABLE_CLIFFORD", "0") == "1"
        if use_clifford:
            self.layout, self.blades = cf.Cl(3)
            self._mock = False
        else:
            # Minimal mock fallback
            self.layout = None
            self.blades = {"e1": 1, "e2": 2, "e3": 3}
            self._mock = True

    def mult(self, a, b):
        if self._mock:
            return a * b  # simple numeric multiplication
        return a * b

    def pretty(self, a):
        return str(a)


# Example usage (to be moved to tests):
# ga = GeometricAlgebra()
# e1 = ga.blades['e1']
# e2 = ga.blades['e2']
# print(ga.mult(e1, e2))
