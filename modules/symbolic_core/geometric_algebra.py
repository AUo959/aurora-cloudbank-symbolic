# geometric_algebra.py
"""
Geometric Algebra utilities for symbolic and quantum-inspired workflows.
Uses the 'clifford' library for core operations if available, otherwise provides a minimal mock implementation.
"""

try:
    import clifford as cf
except Exception:
    cf = None


class GeometricAlgebra:

    def __init__(self):
        if cf is not None:
            self.layout, self.blades = cf.Cl(3)
            self._mock = False
        else:
            # Minimal mock fallback
            self.layout = None
            self.blades = {"e1": 1, "e2": 2, "e3": 3}
            self._mock = True

    def mult(self, a, b):
        if self._mock:
            # Mock implementation for string blade multiplication
            if isinstance(a, str) and isinstance(b, str):
                if a == b:
                    return 1  # e1*e1 = 1
                elif {a, b} == {"e1", "e2"}:
                    return "e12"  # e1*e2 = e12
                elif {a, b} == {"e2", "e3"}:
                    return "e23"  # e2*e3 = e23
                elif {a, b} == {"e1", "e3"}:
                    return "e13"  # e1*e3 = e13
                else:
                    return f"{a}*{b}"
            return a * b  # numeric multiplication
        return a * b

    def pretty(self, a):
        return str(a)


# Example usage (to be moved to tests):
# ga = GeometricAlgebra()
# e1 = ga.blades['e1']
# e2 = ga.blades['e2']
# print(ga.mult(e1, e2))
