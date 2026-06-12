"""
Sensor array tunable constants — single source of truth.

Per spec RQ-3, thresholds belong in ``shared/constants.py`` once the GUMAS
Forge refactor merges. Until then this module is the sensor-local equivalent;
RQ-3 calibration (AFS harness, Brier-scored backtests) tunes values here
without code changes elsewhere. Threshold changes are commits carrying
backtest evidence; quarterly cycle, out-of-cycle only for rupture incidents.

Certainty tags per Canon Protocol:
- [FACT] values mirrored from existing repo surfaces.
- [ASSUMPTION] starting values awaiting RQ-3 calibration.
"""

# --- Drift scale (Δ — dimensionless drift delta) -------------------- [FACT]
DRIFT_THRESHOLD_DELTA = 0.002          # rollback threshold
DRIFT_PRESIG_RATIO = 0.5               # pre-signature alert at 50% of limit
DRIFT_VELOCITY_ALERT = 0.0005          # Δ/hour considered "diverging"
DRIFT_VELOCITY_CONVERGING = -0.0002    # Δ/hour considered "converging"

# --- Ethics / deviation-fraction scale (DriftDetector-owned) -------- [FACT]
# NOTE: these mirror src/monitoring/drift_detector.py defaults. They are
# deviation FRACTIONS, not drift Δ. Never route onto drift dashboards.
DEVIATION_INFO = 0.2
DEVIATION_WARNING = 0.5
DEVIATION_CRITICAL = 0.8

# --- Symbol Integration Index (Lotus §IV) --------------------- [ASSUMPTION]
SII_CORE_THRESHOLD = 0.8               # depth >= core => load-bearing
SII_PERIPHERY_THRESHOLD = 0.2          # depth < periphery => unintegrated
SII_TRANSITIVE_WEIGHT = 0.3            # 1-hop transitive dependent weight
SII_RUPTURE_LOSS_RATE = 0.10           # connection loss/hour for rupture
SII_PERIPHERY_CLUSTER_MIN = 5          # correlated periphery presigs => drift

# --- Resonance ------------------------------------------------ [ASSUMPTION]
RESONANCE_THRESHOLD = 0.7
BLEED_RISK_ALERT = 0.3
RESONANCE_SYNC_WARNING = 0.05          # ZIPWIZ RESONANCE_SYNC divergence
RESONANCE_SYNC_CRITICAL = 0.10

# --- Ethical signal sentinel ---------------------------------- [ASSUMPTION]
SENTINEL_RISK_INTERVENTION = 0.7
SENTINEL_RISK_HUMAN_APPROVAL = 0.8
SENTINEL_RISK_AUDIT = 0.6
SENTINEL_RISK_MONITOR = 0.4
SENTINEL_NEAR_BOUNDARY_MARGIN = 0.2
SENTINEL_ACCEL_VELOCITY = 0.1
SENTINEL_INCREASING_VELOCITY = 0.02
SENTINEL_WEIGHTS = {"tone": 0.25, "boundary": 0.40, "accumulation": 0.35}

# --- Oscillation health --------------------------------------- [ASSUMPTION]
OSC_MAX_CORRECTIONS_PER_HOUR = 20
OSC_ALTERNATION_ALERT = 0.7
OSC_HEALTHY_FREQ = 10
OSC_HEALTHY_SUCCESS = 0.8

# --- Tick lifecycle / budget ---------------------------------- [ASSUMPTION]
DECIMATION_DEFAULT_N = 5               # sample unlisted phases every Nth tick
TICK_BUDGET_FRACTION = 0.10            # aggregate sensor overhead per tick
TICK_BUDGET_FRACTION_MAX = 0.15
QUARANTINE_REVIEW_HOURS = 24

# --- Pattern library (RQ-2) ----------------------------------- [ASSUMPTION]
PATTERN_PROMOTE_PRECISION = 0.7
PATTERN_PROMOTE_MIN_N = 10
PATTERN_DEMOTE_FP_RATE = 0.30
PATTERN_TMINUS_WINDOW_HOURS = 2

# --- Windows ---------------------------------------------------------------
DEFAULT_OBSERVATION_WINDOW_SECONDS = 3600
