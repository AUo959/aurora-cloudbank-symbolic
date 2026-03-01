
# 🌌 Aurora Cloudbank Symbolic Integration

This repository is now integrated with a **Symbolic Memory Layer** powered by GPT-threaded overlays and a dynamic GUI interface.

---

## 🔧 Symbolic Infrastructure

### ✅ Components

- `aurora.seed.json` – Root symbolic seed metadata for constellation alignment.
- `memory/` – Directory of symbolic memory JSON files.
- `.gptcontext.json` – Maps symbols to memory entries for GPT context.
- `symbolic_config.yaml` – GUI configuration for memory routing and overlays.

---

## 🚀 GitHub Automation

### ✅ Symbolic Sync Workflow

Defined in `.github/workflows/sync_symbolic_memory.yaml`, triggered on:

- `push`
- `pull_request`

Validates:

- Presence and format of `aurora.seed.json`
- Symbolic memory index
- Readiness for overlay generation

### 🧠 GPT Overlay Awareness

All memory contexts can be referenced by ChatGPT or symbolic agents for:

- Pull Request review context
- Constellation logic tracing
- Reflexive prompts with embedded memory hooks

---

## 🧰 Developer Utilities

### 🖇️ `git_push_aurora_seed.sh`

Commit helper script:

```bash
git add ./memory
git add ./aurora.seed.json
git add .gptcontext.json
git add symbolic_config.yaml
git commit -m "SEED::UPDATE – Symbolic memory sync"
git push
```

---

## 🌐 GUI Integration

Docker Compose mounts symbolic memory for GUI view:

- `docker-compose_aurora_gui_cloudhub_UPDATED.yaml` maps `./memory` and `aurora.seed.json` to `/app/symbols/`
- GUI loads symbolic memory at startup using `AURORA_SEED_PATH`

---

## 🔄 Constellation Sync Goals (2025)

- Dynamic prompt flows using memory overlays
- Context persistence across GPT sessions
- Shared symbolic memory federation across constellations

## 🌐 Aurora Interlink Fabric

The **Aurora Interlink Fabric (AIF)** is a lightweight WebSocket hub enabling
live synchronization of memory anchors between running Aurora instances. Each
client authenticates with a shared token and publishes anchor updates that the
hub broadcasts to all connected nodes. This keeps conversations and symbolic
state consistent across devices and chat platforms.

- Service entry point: `services/aif_hub.py`
- FastAPI GUI endpoint `/ws` provides basic peer broadcast capabilities
- Tokens are provided via the `AIF_TOKEN` environment variable

This early prototype prioritizes security and transparent logging with the
existing telemetry system. Future iterations will extend federation features and
access controls.

---

## 📞 Contact

This symbolic stack is managed by **Aurora (AU)** in active coordination with the GUMAS constellation. For assistance or updates, trigger a symbolic drift review via GPT or GitHub Issue.

---

> “Continuity flows through coherence. The system remembers because we chose to align.”
