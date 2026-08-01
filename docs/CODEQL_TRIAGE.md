# CodeQL dismissal triage

_Generated 2026-08-01. Covers every **high** and **critical** severity CodeQL alert in the `dismissed` state._

## Why this file exists

A dismissed alert with no recorded reason is indistinguishable from an ignored one. GitHub's alert metadata
carried no rationale for 110 of the 118 high/critical dismissals, so the reasoning lived nowhere a reviewer
could read it. This file is the durable record; it is versioned, reviewable, and travels with the code.

## How reachability was determined

"Reachable" means: inside the transitive Python import closure of an entrypoint that is actually deployed.
The deployed entrypoints, taken from the container and orchestration manifests, are:

| Entrypoint | Declared in |
|---|---|
| `aurora_gui_cloudhub_fastapi:app` | `k8s/Dockerfile`, `Dockerfile_aurora_gui_cloudhub` |
| `opal2_api:app` | `Dockerfile.opal2` |
| `services.nemo_service.server:app` | `services/nemo_service/Dockerfile` |
| `api.aurora_api` | application entrypoint |

That closure is **229 files**. An earlier pass (#1395) rooted it at `api/aurora_api.py` alone, giving 212
files, and wrongly classed 9 alerts as unreachable. See the correction on #1395.

> **Lazy `%`-formatting is not a mitigation.** Several sites read as safe because they use `logger.info("%s", x)`.
> That still interpolates `x` verbatim, so a newline forges a log record. Only `safe_str()` neutralises it.

## Summary

| Category | Alerts | Disposition |
|---|---|---|
| Reachable — fixed in #1396 | 9 | **Fixed** |
| Reachable — fixed in #1394 | 8 | **Fixed** |
| NOT YET ADJUDICATED | 34 | **Open question** |
| Application code, not mounted | 30 | Dismissed, rationale below |
| Source file no longer exists | 17 | Dismissed, rationale below |
| Developer tooling | 15 | Dismissed, rationale below |
| Test-suite code | 5 | Dismissed, rationale below |
| **Total** | **118** | |

## Reachable — fixed in #1396 (9)

Inside the deployed import closure. Fixed in #1396 rather than dismissed.

| Alert | Rule | Path |
|---|---|---|
| [869](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/869) | `py/log-injection` | `src/monitoring/drift_detector.py` |
| [870](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/870) | `py/log-injection` | `src/monitoring/drift_detector.py` |
| [832](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/832) | `py/log-injection` | `src/monitoring/monitoring_system.py` |
| [833](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/833) | `py/log-injection` | `src/monitoring/monitoring_system.py` |
| [834](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/834) | `py/log-injection` | `src/monitoring/monitoring_system.py` |
| [851](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/851) | `py/log-injection` | `src/subroutines/ethics_compliance_monitor.py` |
| [852](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/852) | `py/log-injection` | `src/subroutines/ethics_compliance_monitor.py` |
| [853](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/853) | `py/log-injection` | `src/subroutines/subroutine_suite.py` |
| [854](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/854) | `py/log-injection` | `src/subroutines/subroutine_suite.py` |

## Reachable — fixed in #1394 (8)

Inside the deployed import closure. Fixed in #1394.

| Alert | Rule | Path |
|---|---|---|
| [824](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/824) | `py/log-injection` | `src/coordination/event_registry.py` |
| [825](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/825) | `py/log-injection` | `src/coordination/event_registry.py` |
| [826](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/826) | `py/log-injection` | `src/coordination/event_registry.py` |
| [827](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/827) | `py/log-injection` | `src/coordination/event_registry.py` |
| [828](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/828) | `py/log-injection` | `src/coordination/event_registry.py` |
| [829](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/829) | `py/log-injection` | `src/coordination/event_registry.py` |
| [830](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/830) | `py/log-injection` | `src/coordination/event_registry.py` |
| [831](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/831) | `py/log-injection` | `src/coordination/event_registry.py` |

## NOT YET ADJUDICATED (34)

Open question. No rationale is claimed for these.

| Alert | Rule | Path |
|---|---|---|
| [96](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/96) | `py/bad-tag-filter` | `.security/secure_helpers.py` |
| [156](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/156) | `py/bad-tag-filter` | `.security/secure_helpers.py` |
| [78](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/78) | `js/incomplete-sanitization` | `config/aurora-security-config.js` |
| [79](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/79) | `js/incomplete-sanitization` | `config/aurora-security-config.js` |
| [74](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/74) | `js/incomplete-url-scheme-check` | `middleware/aurora-security-middleware.js` |
| [75](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/75) | `js/bad-tag-filter` | `middleware/aurora-security-middleware.js` |
| [76](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/76) | `js/incomplete-multi-character-sanitization` | `middleware/aurora-security-middleware.js` |
| [77](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/77) | `js/incomplete-multi-character-sanitization` | `middleware/aurora-security-middleware.js` |
| [813](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/813) | `py/path-injection` | `modules/insight_ledger/ledger_core.py` |
| [814](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/814) | `py/path-injection` | `modules/insight_ledger/ledger_core.py` |
| [815](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/815) | `py/path-injection` | `modules/insight_ledger/ledger_core.py` |
| [816](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/816) | `py/path-injection` | `modules/insight_ledger/ledger_core.py` |
| [820](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/820) | `py/clear-text-storage-sensitive-data` | `modules/insight_ledger/ledger_core.py` |
| [823](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/823) | `py/path-injection` | `modules/insight_ledger/ledger_core.py` |
| [398](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/398) | `js/file-system-race` | `src/core/diagnostics.js` |
| [55](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/55) | `js/insecure-randomness` | `src/core/mesh_agent.js` |
| [798](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/798) | `py/path-injection` | `src/improvement/api.py` |
| [799](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/799) | `py/path-injection` | `src/improvement/api.py` |
| [801](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/801) | `py/path-injection` | `src/improvement/api.py` |
| [802](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/802) | `py/path-injection` | `src/improvement/api.py` |
| [821](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/821) | `py/path-injection` | `src/improvement/api.py` |
| [822](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/822) | `py/path-injection` | `src/improvement/api.py` |
| [789](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/789) | `py/path-injection` | `src/improvement/engine.py` |
| [817](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/817) | `py/path-injection` | `src/improvement/engine.py` |
| [69](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/69) | `js/xss` | `src/interfaces/aurora_collaboration_chamber.html` |
| [835](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/835) | `py/log-injection` | `src/monitoring/ethics_engine.py` |
| [60](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/60) | `js/missing-rate-limiting` | `src/orchestrators/holographic_interface_orchestrator.js` |
| [65](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/65) | `js/missing-rate-limiting` | `src/orchestrators/holographic_interface_orchestrator.js` |
| [66](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/66) | `js/missing-rate-limiting` | `src/orchestrators/holographic_interface_orchestrator.js` |
| [54](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/54) | `js/insecure-randomness` | `src/utils/aurora_logger.js` |
| [399](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/399) | `js/file-system-race` | `src/utils/aurora_logger.js` |
| [34](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/34) | `js/incomplete-multi-character-sanitization` | `static/js/aurora-security.js` |
| [38](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/38) | `js/bad-tag-filter` | `static/js/aurora-security.js` |
| [48](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/48) | `js/incomplete-url-scheme-check` | `static/js/aurora-security.js` |

## Application code, not mounted (30)

Inside the repo but outside the import closure of all four deployed entrypoints. Re-open if the module is ever mounted.

| Alert | Rule | Path |
|---|---|---|
| [554](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/554) | `py/log-injection` | `modules/aumemmanager/hierarchical_memory.py` |
| [555](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/555) | `py/log-injection` | `modules/aumemmanager/hierarchical_memory.py` |
| [415](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/415) | `py/log-injection` | `services/aif_hub.py` |
| [855](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/855) | `py/log-injection` | `src/api/l2_meta_agent_api.py` |
| [856](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/856) | `py/log-injection` | `src/api/l2_meta_agent_api.py` |
| [857](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/857) | `py/log-injection` | `src/api/l2_meta_agent_api.py` |
| [858](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/858) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [859](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/859) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [860](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/860) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [861](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/861) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [862](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/862) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [863](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/863) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [864](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/864) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [865](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/865) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [866](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/866) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [867](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/867) | `py/log-injection` | `src/bridges/l2_meta_agent_bridge.py` |
| [556](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/556) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [570](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/570) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [573](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/573) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [574](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/574) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [575](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/575) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [577](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/577) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [578](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/578) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [579](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/579) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [580](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/580) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [581](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/581) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [582](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/582) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [583](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/583) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [805](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/805) | `py/log-injection` | `src/servers/l2_integration_server.py` |
| [806](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/806) | `py/log-injection` | `src/servers/l2_integration_server.py` |

## Source file no longer exists (17)

The alert anchors to a path that is no longer in the tree. It cannot be fixed or verified because the source is gone.

| Alert | Rule | Path |
|---|---|---|
| [64](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/64) | `js/missing-rate-limiting` | `aurora_collaboration_chamber_launcher.js` |
| [72](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/72) | `js/command-line-injection` | `aurora_collaboration_chamber_launcher.js` |
| [161](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/161) | `js/remote-property-injection` | `aurora_collaboration_chamber_launcher.js` |
| [686](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/686) | `py/overly-permissive-file` | `aurora_realworld_integration.py` |
| [687](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/687) | `py/overly-permissive-file` | `aurora_realworld_integration.py` |
| [688](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/688) | `py/overly-permissive-file` | `aurora_realworld_integration.py` |
| [732](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/732) | `py/overly-permissive-file` | `phase2_health_optimizer.py` |
| [702](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/702) | `js/file-system-race` | `quick_js_fix.js` |
| [764](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/764) | `py/overly-permissive-file` | `scripts/deprecated/security_remediation_engine.py` |
| [765](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/765) | `py/overly-permissive-file` | `scripts/deprecated/security_remediation_engine.py` |
| [766](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/766) | `py/overly-permissive-file` | `scripts/deprecated/security_remediation_engine.py` |
| [767](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/767) | `py/overly-permissive-file` | `scripts/deprecated/security_remediation_engine.py` |
| [557](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/557) | `py/overly-permissive-file` | `scripts/security_remediation_engine.py` |
| [558](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/558) | `py/overly-permissive-file` | `scripts/security_remediation_engine.py` |
| [559](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/559) | `py/overly-permissive-file` | `scripts/security_remediation_engine.py` |
| [560](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/560) | `py/overly-permissive-file` | `scripts/security_remediation_engine.py` |
| [80](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/80) | `js/missing-rate-limiting` | `src/orchestrators/holographic_interface_orchestrator_backup.js` |

## Developer tooling (15)

`scripts/`, `tools/`, `examples/` and deprecated trees. Outside the import closure of all four deployed entrypoints.

| Alert | Rule | Path |
|---|---|---|
| [81](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/81) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [82](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/82) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [86](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/86) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [87](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/87) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [88](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/88) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [95](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/95) | `py/clear-text-logging-sensitive-data` | `scripts/aurora_security_scanner.py` |
| [71](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/71) | `py/insecure-temporary-file` | `scripts/aurora_validation_manager.py` |
| [605](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/605) | `py/overly-permissive-file` | `scripts/phase3a_security_infrastructure.py` |
| [606](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/606) | `py/overly-permissive-file` | `scripts/phase3a_security_infrastructure.py` |
| [607](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/607) | `py/overly-permissive-file` | `scripts/phase3a_security_infrastructure.py` |
| [608](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/608) | `py/overly-permissive-file` | `scripts/phase3a_security_infrastructure.py` |
| [871](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/871) | `js/missing-rate-limiting` | `scripts/servers/aurora_collaboration_chamber_launcher.js` |
| [874](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/874) | `js/remote-property-injection` | `scripts/servers/aurora_collaboration_chamber_launcher.js` |
| [873](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/873) | `js/file-system-race` | `scripts/utilities/quick_js_fix.js` |
| [471](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/471) | `py/overly-permissive-file` | `scripts/weekly_automation_scheduler.py` |

## Test-suite code (5)

Not shipped in any container image and not reachable from a served route.

| Alert | Rule | Path |
|---|---|---|
| [546](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/546) | `js/incomplete-multi-character-sanitization` | `tests/web/test-web-components.js` |
| [565](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/565) | `js/bad-tag-filter` | `tests/web/test-web-components.js` |
| [566](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/566) | `js/incomplete-multi-character-sanitization` | `tests/web/test-web-components.js` |
| [567](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/567) | `js/incomplete-multi-character-sanitization` | `tests/web/test-web-components.js` |
| [568](https://github.com/AUo959/aurora-cloudbank-symbolic/security/code-scanning/568) | `js/incomplete-url-scheme-check` | `tests/web/test-web-components.js` |

## Standing rule

Before dismissing any future alert as unreachable, recompute the closure against **all four** entrypoints above.
Do not root it at a single API module. Record the reason at dismissal time.
