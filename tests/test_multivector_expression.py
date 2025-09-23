import pytest

from aurora_api import parse_multivector
from modules.symbolic_core.geometric_algebra import GeometricAlgebra


ga = GeometricAlgebra()


def test_parse_multivector_accepts_negative_decimal():
    result = parse_multivector("-1.5 e1", ga.blades)
    expected = ga.blades["e1"] - 1.5
    assert str(result) == str(expected)


def test_parse_multivector_strips_whitespace():
    result = parse_multivector("  -2.0   e2  ", ga.blades)
    expected = ga.blades["e2"] - 2.0
    assert str(result) == str(expected)


def test_parse_multivector_rejects_invalid_token():
    with pytest.raises(ValueError):
        parse_multivector("e1;rm", ga.blades)
