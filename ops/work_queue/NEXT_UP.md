# NEXT_UP — Aurora Work Queue

*Auto-generated. Do not edit by hand. Source: `ops/work_queue/queue.json`*  
*Last updated: 2026-06-22*

---

## ⛔ Decision required first

These items cannot be started by an agent. They need an explicit operator or Aurora decision.

| # | Task | Blocks |
|---|---|---|
| [#1126](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1126) | Recovered protocols live-manifest and runtime wiring decision | Q-0002 (pentest scope v2) |

---

## 🔴 Ready — CRITICAL

| Queue ID | Issue | Task |
|---|---|---|
| Q-0001 | [#1126](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1126) | Recovered protocols live-manifest decision *(decision_required — operator only)* |

---

## 🟠 Ready — HIGH (agent-safe with context pack)

| Queue ID | Issue | Task |
|---|---|---|
| Q-0004 | [#1127](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1127) | Architecture layer terminology corrections |
| Q-0005 | [#1124](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1124) | QGIA_SIM_BRIDGE canonicalization |

---

## 🔒 Blocked — waiting on Q-0001

| Queue ID | Issue | Waiting on |
|---|---|---|
| Q-0002 | [#1130](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1130) | Q-0001 (recovered protocols decision) |
| Q-0003 | [#1129](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1129) | Q-0002 (pentest scope v2) |

---

## 🟡 Ready — MEDIUM (agent-safe)

| Queue ID | Issue | Task |
|---|---|---|
| Q-0006 | [#1128](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1128) | API reference authority clarification |

---

*If you are an LLM or agent: read the `context_pack` for your chosen task in `queue.json` before starting. Do not start blocked or decision_required tasks.*
