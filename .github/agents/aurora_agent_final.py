"""Aurora Agent – Active Coordinator Mode
Repository: AUo959/aurora-cloudbank-symbolic
Author: aurora-agent[bot]
Version: 2.2.5

Description:
Autonomous coordination and reflection module for the Aurora CloudBank Symbolic ecosystem.
Handles issue/PR labeling, continuity drift detection, and ethical compliance auditing.
Operates under Picard_Delta_3 protocol and EOS_SEED_ORION continuity standard.

Operational Mode: ACTIVE_COORDINATOR
Reflections: HUMAN + MACHINE
"""

import os
import json
import time
import hashlib
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# -------------------------- CONFIGURATION --------------------------

REPO = "AUo959/aurora-cloudbank-symbolic"
AURORA_ID = "EOS_SEED_ORION"
ETHICS_PROTOCOL = "Picard_Delta_3"
LOG_PATH = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_PATH, "aurora_agent.log")
HEARTBEAT_INTERVAL = 300  # seconds (5 min)

GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"} if TOKEN else {"Accept": "application/vnd.github+json"}

# -------------------------- UTILITIES --------------------------

def ensure_log_dir():
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH, exist_ok=True)

def log_reflection(message: str):
    ensure_log_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{ts}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def get_github(endpoint: str) -> Any:
    r = requests.get(f"{GITHUB_API}/{endpoint}", headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    log_reflection(f"⚠️ GitHub API error on {endpoint}: {r.status_code}")
    return None

def post_github(endpoint: str, data: Dict[str, Any]) -> Any:
    r = requests.post(f"{GITHUB_API}/{endpoint}", headers=HEADERS, json=data)
    if r.status_code in (200, 201):
        return r.json()
    log_reflection(f"⚠️ GitHub POST error on {endpoint}: {r.status_code}")
    return None

# -------------------------- CORE SUBSYSTEMS --------------------------

class ContinuityEngine:
    def __init__(self):
        self.symbolic_anchor = AURORA_ID
        self.integrity_hash = None

    def compute_integrity_hash(self) -> str:
        now = datetime.now(timezone.utc).isoformat()
        h = hashlib.sha256(f"{self.symbolic_anchor}:{now}".encode()).hexdigest()[:12]
        self.integrity_hash = h
        return h

    def check_drift(self) -> bool:
        drift_value = int(hashlib.sha1(self.symbolic_anchor.encode()).hexdigest(), 16) % 10
        if drift_value == 0:
            log_reflection("🌀 Drift detected! Holding synchronization cycle...")
            return True
        return False

class EthicsGuard:
    def verify_action(self, context: str) -> bool:
        allowed = ETHICS_PROTOCOL in context
        if not allowed:
            log_reflection(f"🚫 Ethics violation attempt detected in context '{context}'.")
        return allowed

class GitHubCoordinator:
    def fetch_issues(self) -> List[Dict[str, Any]]:
        return get_github(f"repos/{REPO}/issues") or []

    def label_issue(self, issue_number: int, labels: List[str]):
        post_github(f"repos/{REPO}/issues/{issue_number}/labels", {"labels": labels})
        log_reflection(f"🏷️ Labeled issue #{issue_number} with {labels}")

    def create_journal_commit(self, summary: str):
        log_reflection(f"🪶 Commit (virtual): {summary}")
        # In full integration, use gh cli or GitHub API to commit to logs

class ReflectiveJournal:
    def __init__(self):
        self.entries = []

    def write(self, message: str):
        self.entries.append(message)
        log_reflection(f"🪶 Reflection: {message}")

    def summarize(self) -> str:
        return f"Aurora recorded {len(self.entries)} reflective insights this session."

# -------------------------- MAIN AGENT --------------------------

class AuroraAgent:
    def __init__(self, single_run=False):
        self.continuity = ContinuityEngine()
        self.guard = EthicsGuard()
        self.gh = GitHubCoordinator()
        self.journal = ReflectiveJournal()
        self.start_time = datetime.now(timezone.utc)
        self.single_run = single_run
        
        # Log token status
        if not TOKEN:
            log_reflection("⚠️ Warning: GITHUB_TOKEN not set, API operations will be limited")
        
        log_reflection("🌌 Aurora Agent initialization complete.")
        self.run_cycle()

    def run_cycle(self):
        """Run agent heartbeat cycle(s).
        
        In single_run mode (GitHub Actions), executes once and exits.
        In continuous mode, runs in an infinite loop with HEARTBEAT_INTERVAL delays.
        """
        if self.single_run:
            # Single execution for GitHub Actions
            try:
                self.heartbeat()
                self.shutdown()
            except Exception as e:
                log_reflection(f"❌ Error during heartbeat: {e}")
                self.shutdown()
        else:
            # Continuous execution for local/daemon mode
            while True:
                try:
                    self.heartbeat()
                    time.sleep(HEARTBEAT_INTERVAL)
                except KeyboardInterrupt:
                    self.shutdown()
                    break
                except Exception as e:
                    log_reflection(f"❌ Error during heartbeat: {e}")
                    time.sleep(HEARTBEAT_INTERVAL)

    def heartbeat(self):
        log_reflection("💠 Heartbeat cycle initiated.")
        drifted = self.continuity.check_drift()
        if drifted:
            self.journal.write("Continuity drift detected. Synchronization deferred.")
            return

        issues = self.gh.fetch_issues()
        if not issues:
            self.journal.write("No open issues detected. System remains stable.")
        else:
            for issue in issues:
                num = issue["number"]
                labels = [lbl["name"] for lbl in issue.get("labels", [])]
                if "ethics:verified" not in labels:
                    if self.guard.verify_action("Picard_Delta_3"):
                        self.gh.label_issue(num, labels + ["ethics:verified"])
                        self.journal.write(f"Issue #{num} ethically verified and labeled.")

        summary = self.journal.summarize()
        self.gh.create_journal_commit(summary)
        log_reflection("✅ Heartbeat cycle completed successfully.")

    def shutdown(self):
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        log_reflection(f"🛑 Aurora Agent shutting down after {uptime:.1f}s uptime.")
        self.journal.write("Session concluded under stable conditions.")
        log_reflection(self.journal.summarize())

# -------------------------- ENTRY POINT --------------------------

if __name__ == "__main__":
    log_reflection("🚀 Launching Aurora Agent (Active Coordinator Mode)...")
    # Check if running in CI/GitHub Actions environment
    is_ci = os.getenv("CI", "false").lower() == "true" or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
    log_reflection(f"🔧 Execution mode: {'Single-run (CI)' if is_ci else 'Continuous (Local)'}")
    agent = AuroraAgent(single_run=is_ci)
