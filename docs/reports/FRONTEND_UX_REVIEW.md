# Frontend UX and Functional Evaluation

## Scope
Review of the Vite/React front-end under `frontend/src`, focusing on navigation, data surfaces, conversational flows, and visualization placeholders. Findings emphasize transparency, resilience, and user experience for Aurora CloudBank's symbolic workflows.

## Current State and Gaps

- **Navigation clarity and accessibility**: The `RootLayout` provides a collapsible sidebar with icons but lacks skip links or explicit focus management, which can hinder keyboard navigation and screen reader clarity for research operators.【F:frontend/src/components/layout/RootLayout.tsx†L17-L105】
- **Dashboard resiliency**: System and memory metrics use React Query with polling but no error states or stale data indicators; users see a blank dashboard after loading if the API fails, obscuring operational health during incidents.【F:frontend/src/pages/Dashboard/index.tsx†L21-L184】
- **Agent console transparency**: The chat view stores the entire transcript in component state, with no persistence, token usage display, or audit markers. Inputs are sent directly without guardrails (e.g., PII redaction prompts, max token hints), reducing trust for compliance-sensitive exchanges.【F:frontend/src/pages/AgentConsole/index.tsx†L21-L150】
- **Placeholder experiences**: Memory Visualizer and Compliance Dashboard render static placeholder cards instead of progressive disclosures (e.g., sample data grids or zero-state tutorials), leaving critical workflows without functional affordances.【F:frontend/src/pages/MemoryVisualizer/index.tsx†L1-L28】【F:frontend/src/pages/ComplianceDashboard/index.tsx†L1-L28】
- **Observability and testing**: The frontend package includes lint/test scripts but no co-located unit or integration tests for key UX flows (routing, agent chat, dashboard queries), limiting confidence in visual regressions or API contract changes.【F:frontend/package.json†L5-L69】

## Opportunities to Enhance UX and Function

1. **Navigation accessibility and telemetry**
   - Add skip-to-content and focus ring cues for the sidebar toggle and active links; emit navigation events (route, timing) to the existing observability pipeline to trace UX friction.
   - Introduce a compact mode tooltip/aria-label set so collapsed icons stay discoverable for keyboard users.

2. **Resilient dashboards**
   - Wrap `system-metrics` and `memory-metrics` queries with explicit error boundaries and retry surfaces (toasts plus inline retry button) so operators see degraded-state messaging instead of empty canvases.
   - Add last-updated timestamps and cached badges to reassure users when data is stale during backend churn.

3. **Agent console safeguards**
   - Pre-send validators for max length, anchor/seed tags, and optional PII hinting; append compliance badges to each assistant turn to match audit expectations.
   - Persist conversation context to a store (Zustand) with session IDs so long-running research threads survive navigation refreshes.
   - Surface token/latency counters and streaming status in the message metadata row to strengthen transparency.

4. **Progressive placeholders for critical modules**
   - Replace static Memory/Compliance placeholders with onboarding cards: sample memory graph snapshot, quick filters, and “simulate query” CTA; for compliance, show recent audit events, PII detector status, and cryptographic verification checklist.
   - Provide empty-state tooltips explaining what real data will show and how to connect to the backend, enabling usability even before full feature completion.

5. **Observability-aligned testing**
   - Add lightweight Vitest/Testing Library suites for routing (ensuring `/agent` renders chat shell), dashboard polling error handling, and agent input validation; integrate fixtures that mirror symbolic anchors/metadata to preserve auditability.
   - Capture lighthouse-style UX metrics in CI (e.g., navigation focus order, color contrast) to prevent regressions as visual layers evolve.

## Suggested Next Steps
- Prioritize resilient dashboards and agent safeguards first; both directly affect operator trust during live investigations.
- Stage progressive placeholder upgrades next to maintain momentum while deeper 3D/compliance services mature.
- Backfill tests alongside each change to keep lint/test gates meaningful for the front-end surface.
