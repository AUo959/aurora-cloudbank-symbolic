# test_geometric_algebra.py
from modules.symbolic_core.geometric_algebra import GeometricAlgebra


def test_blade_multiplication():
    pass
    ga = GeometricAlgebra()
    e1 = ga.blades["e1"]
    e2 = ga.blades["e2"]
    result = ga.mult(e1, e2)
    assert str(result) == str(e1 * e2)


def test_pretty():
    pass
    ga = GeometricAlgebra()
    e1 = ga.blades["e1"]
    assert ga.pretty(e1) == str(e1)
