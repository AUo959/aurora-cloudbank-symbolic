# Quantum Decision Oracle

This feature module predicts probabilistic outcomes for scenario dictionaries and
records reproducible audit trails. Its public API is `QuantumDecisionOracle` and
the related result and mode types exported from this package.

It is intentionally distinct from
`tools/simulation_engine/quantum_decision_oracle.py`, whose contract ranks
explicit alternatives against weighted criteria. The shared class name does not
make the implementations interchangeable.

New consumers should import from `modules.quantum_decision_oracle`. The legacy
`src.quantum_decision_oracle` path remains a compatibility import; removal would
require separate approval.
