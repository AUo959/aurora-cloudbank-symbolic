# Aurora Load Testing Harness

Locust-based load testing for Aurora CloudBank Symbolic. Validates that production endpoints meet the SLOs documented in `slo_baselines.json`.

## Quick Start

```bash
# Install locust (already in requirements-dev.txt)
pip install locust>=2.32.0

# Start the Aurora API server
python api/aurora_api.py &

# Run standard baseline (50 users, 60 s, headless)
locust -f tests/load/locustfile.py \
       --host=http://localhost:8000 \
       --users=50 \
       --spawn-rate=5 \
       --run-time=60s \
       --headless

# Or use the interactive web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 in a browser
```

## User Classes

| Class | Profile | Use case |
|---|---|---|
| `AuroraAPIUser` | `wait_time=between(0.5, 2.0)` | Standard mixed read/write baseline |
| `AuroraHighLoadUser` | `constant_throughput(5 rps/user)` | Stress / soak testing |
| `AuroraQuantumUser` | `wait_time=between(1.0, 5.0)` | Quantum simulator SLO validation |

Run a specific class with `--class AuroraHighLoadUser`.

## Task Weights (AuroraAPIUser)

| Endpoint | Weight | SLO target |
|---|---|---|
| `GET /health` | 10 | p95 < 50 ms, err < 0.1% |
| `POST /memory/retrieve` | 8 | p95 < 500 ms, err < 1% |
| `POST /memory/create` | 4 | p95 < 300 ms, err < 1% |
| `GET /api/health` | 3 | p95 < 50 ms |
| `GET /memory/metrics` | 3 | p95 < 100 ms |
| `GET /telemetry/snapshot` | 3 | p95 < 200 ms |
| `GET /memory/health` | 2 | p95 < 100 ms |
| `GET /metrics` | 2 | p95 < 100 ms |
| `GET /api/synergy/health` | 2 | p95 < 200 ms |
| `GET /simulate/scenarios` | 2 | p95 < 100 ms |
| `GET /simulate/cache/stats` | 2 | p95 < 100 ms |
| `GET /api/drift/patterns` | 1 | p95 < 300 ms |

## SLO Baselines

See `slo_baselines.json` for the full documented targets including:
- p95 latency (ms) per endpoint
- Max acceptable error rate (%)
- Notes on expected behavior and tradeoffs

Re-run and update the baselines after significant changes to core paths (memory, quantum, telemetry).

## Saving Results

```bash
# Save a CSV report
locust -f tests/load/locustfile.py \
       --host=http://localhost:8000 \
       --users=50 --spawn-rate=5 --run-time=60s --headless \
       --csv=tests/load/results/baseline_$(date +%Y%m%d)

# The above produces:
#   results/baseline_YYYYMMDD_stats.csv
#   results/baseline_YYYYMMDD_failures.csv
#   results/baseline_YYYYMMDD_exceptions.csv
```

## CI Integration

Load tests are **not** run in standard CI (too slow / require a live server). Run them:

- Manually before major releases
- In a dedicated performance pipeline with a staging environment
- After any change to core memory, quantum, or telemetry paths

## Troubleshooting

**`ModuleNotFoundError: No module named 'locust'`**
```bash
pip install locust>=2.32.0
```

**Connection refused at localhost:8000**
Make sure the Aurora API server is running:
```bash
python api/aurora_api.py
```

**High error rates on authenticated endpoints**
Most write endpoints require CSRF tokens and authentication. The locust tasks target public and semi-public endpoints by design. Add auth headers to tasks if you need to test protected endpoints.
