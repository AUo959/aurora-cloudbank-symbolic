# Aurora NeMo Service

<!-- Symbolic Anchor: T1 -->
<!-- SRB: NEMO_SERVICE_v1 -->
<!-- DLP: [nemo, inference, gpu, models] -->
<!-- Chain Notation: #SERVICES//NEMO//README// -->
<!-- Ethics Protocol: Picard_Delta_3 -->
<!-- Anchor Seed: EOS_SEED_ORION -->

NVIDIA NeMo inference service fully integrated with the **Aurora/GUMAS symbolic simulation ecosystem**.  Provides ASR, NLU, TTS, and LLM inference with entropy-state reporting, drift detection, and SHA256-sealed simulation snapshots.

---

## Contents

- [Purpose & Anchor Info](#purpose--anchor-info)
- [Endpoint Reference](#endpoint-reference)
- [Example Usage](#example-usage)
- [Docker Build & Run](#docker-build--run)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Symbolic Bridge Integration](#symbolic-bridge-integration)
- [Snapshot / Restore Workflow](#snapshot--restore-workflow)
- [DLP Classification Notes](#dlp-classification-notes)
- [Module Files](#module-files)

---

## Purpose & Anchor Info

| Field | Value |
|-------|-------|
| Module ID | `AURORA_NEMO_SERVICE` |
| Version | `1.0.0` |
| Anchor Seed | `EOS_SEED_ORION` |
| Ethics Protocol | `Picard_Delta_3` |
| SRB Tag | `NEMO_SERVICE_v1` |
| Chain Notation | `#SERVICES//NEMO//` |
| Port | `8090` |
| Container User | `aurora` (UID 1000) |

---

## Endpoint Reference

| Method | Path | DLP | Description |
|--------|------|-----|-------------|
| `GET` | `/nemo/health` | public | Health check with entropy-state and memory-drift |
| `GET` | `/nemo/status` | internal | Model info, GPU utilisation, symbolic anchor state |
| `POST` | `/nemo/infer` | internal | ASR / NLU / TTS inference |
| `POST` | `/nemo/generate` | internal | LLM text generation |
| `POST` | `/nemo/snapshot` | confidential | Create SHA256-sealed simulation snapshot |
| `POST` | `/nemo/restore` | confidential | Restore state from snapshot |

---

## Example Usage

### Health check

```bash
curl http://localhost:8090/nemo/health
```

```json
{
  "status": "ok",
  "service": "aurora-nemo-service",
  "ethics_protocol": "Picard_Delta_3",
  "anchor_seed": "EOS_SEED_ORION",
  "srb": "NEMO_SERVICE_v1",
  "t1": 42,
  "model_loaded": true,
  "entropy_state": { "entropy_value": 0.693, "drift_flagged": false },
  "memory_drift": false
}
```

### Inference

```bash
curl -X POST http://localhost:8090/nemo/infer \
  -H 'Content-Type: application/json' \
  -d '{"text": "Classify this message", "model_type": "nlu"}'
```

### Text generation

```bash
curl -X POST http://localhost:8090/nemo/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Aurora CloudBank is", "max_tokens": 128}'
```

### Create snapshot

```bash
curl -X POST http://localhost:8090/nemo/snapshot \
  -H 'Content-Type: application/json' \
  -d '{"description": "pre-finetune checkpoint"}'
```

### Restore snapshot

```bash
curl -X POST http://localhost:8090/nemo/restore \
  -H 'Content-Type: application/json' \
  -d '{"snapshot_id": "<UUID returned by snapshot endpoint>"}'
```

---

## Docker Build & Run

### Build

```bash
# From the repository root
docker build \
  -f services/nemo_service/Dockerfile \
  -t aurora-nemo-service:latest \
  .
```

### Run (GPU)

```bash
docker run --gpus all \
  -p 8090:8090 \
  -v /path/to/models:/models:ro \
  -v /path/to/snapshots:/snapshots \
  -e NEMO_DEFAULT_MODEL_PATH=/models/my_model.nemo \
  aurora-nemo-service:latest
```

### Run (CPU / no GPU — for development / testing)

```bash
docker run \
  -p 8090:8090 \
  -e NVIDIA_VISIBLE_DEVICES="" \
  aurora-nemo-service:latest
```

### Docker Compose (with GPU)

```bash
# From the services/ directory
docker compose up nemo_service
```

---

## Kubernetes Deployment

### Prerequisites

- GPU node pool with `accelerator: nvidia-gpu` label
- NVIDIA device plugin installed
- `aurora-cloudbank` namespace created (see `k8s/aurora-namespace-rbac.yaml`)

### Deploy

```bash
kubectl apply -f k8s/aurora-nemo-deployment.yaml
kubectl apply -f k8s/aurora-nemo-service.yaml
```

### Verify

```bash
kubectl -n aurora-cloudbank get pods -l app=aurora-nemo-service
kubectl -n aurora-cloudbank logs -l app=aurora-nemo-service -f
```

### Internal service URL

```
http://aurora-nemo-service.aurora-cloudbank.svc.cluster.local:8090
```

---

## Symbolic Bridge Integration

The `SymbolicBridge` class (`symbolic_bridge.py`) connects NeMo inference to Aurora's symbolic engine:

- **Anchor resolution** — advances the T1 temporal anchor on every call and embeds the full anchor context in responses
- **Entropy logging** — measures Shannon entropy over model output distributions; logs each reading with a call index
- **Drift detection** — flags readings whose entropy deviates from the baseline by more than `drift_threshold` (default 0.15)
- **Memory sealing** — computes SHA256 seals over context payloads for continuity verification

All inference responses include an `anchor_context` field with `t1`, `srb`, `anchor_seed`, `ethics_protocol`, and a `chain_notation` string like `#SERVICES//NEMO//LLM//T1:42//`.

---

## Snapshot / Restore Workflow

1. **Create snapshot** — `POST /nemo/snapshot`  returns `snapshot_id` + `seal` (SHA256 hex)
2. **Inspect** — the snapshot JSON is persisted under `NEMO_SNAPSHOTS_DIR` (default `/tmp/nemo_snapshots`)
3. **Verify** — the `StateManager.verify_snapshot()` method recomputes the SHA256 seal and compares it to the stored value; any tampering is detected
4. **Restore** — `POST /nemo/restore` with the `snapshot_id`; the seal is re-verified before the data is returned

This supports **time-travel debugging**: you can create a snapshot before a fine-tuning run, observe the results, and roll back if the outputs diverge.

---

## DLP Classification Notes

| Endpoint | Classification | Rationale |
|----------|---------------|-----------|
| `/nemo/health` | public | No model data exposed |
| `/nemo/status` | internal | Module metadata, anchor state |
| `/nemo/infer` | internal | Input/output may contain sensitive text |
| `/nemo/generate` | internal | Prompts and generated text |
| `/nemo/snapshot` | confidential | Full service state including model config |
| `/nemo/restore` | confidential | Restores confidential state |

Set `NEMO_DLP_CLASSIFICATION` environment variable to override the default (`internal`).

---

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module init with metadata manifest |
| `config.py` | Configuration management, model paths, GPU, anchor seeds |
| `symbolic_bridge.py` | Aurora symbolic engine bridge |
| `state_manager.py` | SHA256 hash-sealed snapshot/restore |
| `server.py` | FastAPI inference server |
| `manifest.json` | Structured metadata manifest |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | GPU-capable multi-stage build |
| `README.md` | This file |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEMO_HOST` | `0.0.0.0` | Bind host |
| `NEMO_PORT` | `8090` | Bind port |
| `NEMO_MODELS_DIR` | `/models` | Model checkpoints directory |
| `NEMO_SNAPSHOTS_DIR` | `/tmp/nemo_snapshots` | Snapshot storage directory |
| `NEMO_DEFAULT_MODEL_PATH` | _(none)_ | Path to default `.nemo` checkpoint |
| `NEMO_DEFAULT_MODEL_TYPE` | `llm` | Default model type (`asr`/`nlu`/`tts`/`llm`) |
| `NEMO_ANCHOR_SEED` | `EOS_SEED_ORION` | Symbolic anchor seed |
| `AURORA_MODULE_ID` | `AURORA_NEMO_SERVICE` | Aurora module identifier |
| `AURORA_ETHICS_PROTOCOL` | `Picard_Delta_3` | Ethics protocol |
| `NVIDIA_VISIBLE_DEVICES` | `all` | GPU visibility |
| `NEMO_DRIFT_THRESHOLD` | `0.15` | Entropy drift alert threshold |
