"""
Tests for quantum mixed-state operations (issue #762).

Verifies that QuantumState.measure(), .entropy(), and .fidelity_with()
work correctly for mixed states (density matrices) in addition to
pure states, and that no raw NotImplementedError is raised.
"""

import math

import numpy as np
import pytest

from modules.quantum_simulator.quantum_state import (
    QuantumState,
    StateVector,
    _matrix_sqrt,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def maximally_mixed_1qubit() -> QuantumState:
    """Return the 1-qubit maximally mixed state ρ = I/2."""
    rho = np.eye(2, dtype=complex) / 2.0
    return QuantumState.from_density_matrix(rho)


def maximally_mixed_2qubit() -> QuantumState:
    """Return the 2-qubit maximally mixed state ρ = I/4."""
    rho = np.eye(4, dtype=complex) / 4.0
    return QuantumState.from_density_matrix(rho)


def pure_zero_1qubit() -> QuantumState:
    """Return |0⟩ as a QuantumState backed by a density matrix."""
    rho = np.array([[1, 0], [0, 0]], dtype=complex)
    return QuantumState.from_density_matrix(rho)


# ---------------------------------------------------------------------------
# _matrix_sqrt helper
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_matrix_sqrt_identity():
    """sqrt(I) = I."""
    result = _matrix_sqrt(np.eye(2, dtype=complex))
    np.testing.assert_allclose(result, np.eye(2), atol=1e-10)


@pytest.mark.unit
@pytest.mark.quantum
def test_matrix_sqrt_diagonal():
    """sqrt of a diagonal matrix squares back correctly."""
    diag = np.diag([4.0, 9.0]).astype(complex)
    root = _matrix_sqrt(diag)
    np.testing.assert_allclose(root @ root, diag, atol=1e-10)


# ---------------------------------------------------------------------------
# from_density_matrix constructor
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_from_density_matrix_mixed_state():
    """from_density_matrix marks is_pure=False for a genuine mixed state."""
    state = maximally_mixed_1qubit()
    assert not state.is_pure
    assert state.num_qubits == 1


@pytest.mark.unit
@pytest.mark.quantum
def test_from_density_matrix_pure_state():
    """from_density_matrix marks is_pure=True when purity ≈ 1."""
    state = pure_zero_1qubit()
    assert state.is_pure


@pytest.mark.unit
@pytest.mark.quantum
def test_from_density_matrix_bad_dimension():
    """from_density_matrix rejects non-power-of-2 dimensions."""
    with pytest.raises(ValueError, match="power of 2"):
        QuantumState.from_density_matrix(np.eye(3, dtype=complex) / 3)


@pytest.mark.unit
@pytest.mark.quantum
def test_from_density_matrix_not_square():
    """from_density_matrix rejects non-square matrices."""
    with pytest.raises(ValueError):
        QuantumState.from_density_matrix(np.ones((2, 4), dtype=complex))


# ---------------------------------------------------------------------------
# from_pure_ensemble constructor
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_from_pure_ensemble_creates_mixed_state():
    """Equal mixture of |0⟩ and |1⟩ produces the maximally mixed 1-qubit state."""
    s0 = QuantumState.from_computational_basis("0")
    s1 = QuantumState.from_computational_basis("1")
    mixed = QuantumState.from_pure_ensemble([(s0, 0.5), (s1, 0.5)])
    expected = np.eye(2, dtype=complex) / 2.0
    np.testing.assert_allclose(mixed.density_matrix, expected, atol=1e-10)
    assert not mixed.is_pure


@pytest.mark.unit
@pytest.mark.quantum
def test_from_pure_ensemble_bad_probabilities():
    """from_pure_ensemble rejects ensembles whose probabilities don't sum to 1."""
    s0 = QuantumState.from_computational_basis("0")
    with pytest.raises(ValueError, match="sum to 1"):
        QuantumState.from_pure_ensemble([(s0, 0.3), (s0, 0.3)])


# ---------------------------------------------------------------------------
# density_matrix property
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_density_matrix_pure_state():
    """Pure |0⟩ state vector produces correct density matrix |0⟩⟨0|."""
    state = QuantumState.from_computational_basis("0")
    rho = state.density_matrix
    expected = np.array([[1, 0], [0, 0]], dtype=complex)
    np.testing.assert_allclose(rho, expected, atol=1e-10)


@pytest.mark.unit
@pytest.mark.quantum
def test_density_matrix_bell_state():
    """Bell state |Φ+⟩ density matrix is rank-1 Hermitian."""
    state = QuantumState.bell_state("phi_plus")
    rho = state.density_matrix
    assert rho.shape == (4, 4)
    # Rank-1 ↔ Tr(ρ²) = 1
    purity = np.real(np.trace(rho @ rho))
    assert abs(purity - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# measure — mixed states
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_measure_mixed_state_no_exception():
    """measure() on a mixed state must not raise NotImplementedError."""
    state = maximally_mixed_1qubit()
    counts, probs = state.measure(num_shots=1000, seed=0)
    assert isinstance(counts, dict)
    assert isinstance(probs, dict)


@pytest.mark.unit
@pytest.mark.quantum
def test_measure_mixed_state_probabilities_sum_to_one():
    """Measurement probabilities of a mixed state sum to 1."""
    state = maximally_mixed_1qubit()
    _, probs = state.measure(num_shots=1000, seed=0)
    assert abs(sum(probs.values()) - 1.0) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_measure_maximally_mixed_uniform_distribution():
    """Maximally mixed 1-qubit state → each basis state ~50% probability."""
    state = maximally_mixed_1qubit()
    _, probs = state.measure()
    assert abs(probs.get("|0⟩", 0) - 0.5) < 1e-6
    assert abs(probs.get("|1⟩", 0) - 0.5) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_measure_mixed_state_reproducible_with_seed():
    """Same seed produces same counts for a mixed state."""
    state = maximally_mixed_1qubit()
    counts1, _ = state.measure(num_shots=500, seed=42)
    counts2, _ = state.measure(num_shots=500, seed=42)
    assert counts1 == counts2


@pytest.mark.unit
@pytest.mark.quantum
def test_measure_mixed_state_2qubit():
    """Measure a 2-qubit mixed state — correct number of labels returned."""
    state = maximally_mixed_2qubit()
    counts, probs = state.measure(num_shots=400, seed=7)
    assert len(probs) == 4
    assert abs(sum(probs.values()) - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# entropy — mixed states
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_mixed_state_no_exception():
    """entropy() on a mixed state must not raise NotImplementedError."""
    state = maximally_mixed_1qubit()
    result = state.entropy()
    assert isinstance(result, float)


@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_maximally_mixed_1qubit():
    """Maximally mixed 1-qubit state has entropy = 1 bit."""
    state = maximally_mixed_1qubit()
    assert abs(state.entropy() - 1.0) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_maximally_mixed_2qubit():
    """Maximally mixed 2-qubit state has entropy = 2 bits."""
    state = maximally_mixed_2qubit()
    assert abs(state.entropy() - 2.0) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_pure_state_is_zero():
    """Pure state |0⟩ has Von Neumann entropy = 0."""
    state = QuantumState.from_computational_basis("0")
    assert abs(state.entropy()) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_pure_state_via_density_matrix():
    """Pure state represented as density matrix also has entropy ≈ 0."""
    state = pure_zero_1qubit()
    assert abs(state.entropy()) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_entropy_partial_mixture():
    """60/40 mixture has entropy strictly between 0 and 1."""
    s0 = QuantumState.from_computational_basis("0")
    s1 = QuantumState.from_computational_basis("1")
    mixed = QuantumState.from_pure_ensemble([(s0, 0.6), (s1, 0.4)])
    entropy = mixed.entropy()
    assert 0.0 < entropy < 1.0


# ---------------------------------------------------------------------------
# fidelity_with — mixed states
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_mixed_states_no_exception():
    """fidelity_with() must not raise NotImplementedError for mixed states."""
    s1 = maximally_mixed_1qubit()
    s2 = maximally_mixed_1qubit()
    result = s1.fidelity_with(s2)
    assert isinstance(result, float)


@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_identical_mixed_states():
    """Fidelity of a mixed state with itself is 1."""
    state = maximally_mixed_1qubit()
    assert abs(state.fidelity_with(state) - 1.0) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_pure_vs_pure_unchanged():
    """Pure–pure fidelity via fidelity_with still works correctly."""
    s0 = QuantumState.from_computational_basis("0")
    s1 = QuantumState.from_computational_basis("1")
    assert abs(s0.fidelity_with(s0) - 1.0) < 1e-6
    assert abs(s0.fidelity_with(s1)) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_pure_vs_mixed():
    """Fidelity of pure |0⟩ with maximally mixed state = 0.5."""
    s_pure = QuantumState.from_computational_basis("0")
    s_mixed = maximally_mixed_1qubit()
    fid = s_pure.fidelity_with(s_mixed)
    assert abs(fid - 0.5) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_mixed_vs_pure():
    """Fidelity is symmetric: F(ρ,σ) = F(σ,ρ)."""
    s_pure = QuantumState.from_computational_basis("0")
    s_mixed = maximally_mixed_1qubit()
    assert abs(s_pure.fidelity_with(s_mixed) - s_mixed.fidelity_with(s_pure)) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_fidelity_in_range():
    """Fidelity must be in [0, 1] for arbitrary states."""
    s0 = QuantumState.from_computational_basis("0")
    s1 = QuantumState.from_computational_basis("1")
    mixed = QuantumState.from_pure_ensemble([(s0, 0.7), (s1, 0.3)])
    fid = mixed.fidelity_with(s0)
    assert 0.0 <= fid <= 1.0 + 1e-9
