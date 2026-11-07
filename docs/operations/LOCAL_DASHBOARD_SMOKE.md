# Local dashboard/API smoke check

The frontend defaults to the same origin for API requests. During development,
Vite forwards `/api` to `http://localhost:8000`. For a separately hosted frontend,
set `VITE_API_BASE_URL` explicitly and configure the deployment's CORS policy.
An empty API base is intentional for local Vite and reverse-proxy deployments.

Start the canonical `api.aurora_api:app` service and Vite (`frontend/npm run dev`).
Configure the existing required local secrets through environment settings;
do not commit them. The check performed on 2026-11-07 used temporary
process-local signing secrets, not production or provider credentials.

## Read-only contract

`GET /api/system/metrics` is rate limited to 60/minute and returns a timestamp,
`memory`, `quantum`, `agents`, `system`, and context tag
`dashboard_metrics_snapshot`. It never starts simulations, agent tasks, or AI
requests. Sources are the running memory manager, tracked simulation statuses,
crew-agent runtime registry, psutil resource observations, and the existing
60-second HTTP metrics window. Counts are process-local, not persistent or
cross-worker totals. Registry counts describe initialized runtime agents, not
a canon personnel census.

Unmeasured `memory.cache_hit_rate` and `quantum.average_speedup` are `null`.
Response latency is `null` before request samples exist. The UI labels them
unavailable and reports API connectivity rather than claiming optimal health.
The activity examples remain explicitly illustrative.

## Reproduced browser checks

- Open `/` on Vite and wait for **Aurora Dashboard** and **Connected**.
- Dashboard metrics requests to `/api/system/metrics` return 200.
- Fetch `/api/health` through Vite: 200, healthy service response.
- Fetch `/api/ai/models` through Vite: 200, `gpt-4.available` is false.
- No JavaScript page errors; unmeasured values display unavailable.
- Frontend production build and strict lint pass.

This verifies the local read path. It does not exercise paid inference,
authenticated mutations, sandbox execution, or hosted production services.
